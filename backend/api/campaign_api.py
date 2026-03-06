from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List

from database import get_db
from models import Campaign, CampaignRun, AgentLog, PerformanceMetric
from schemas import (
    CampaignBriefRequest, 
    CampaignResponse, 
    AgentLogResponse, 
    CampaignRunResponse,
    CampaignInsightResponse
)

from orchestrator.agent_orchestrator import AgentOrchestrator
from services.campaign_service import CampaignService
from services.insight_service import InsightService
from services.segment_intelligence_service import SegmentIntelligenceService
from services.historical_learning_service import HistoricalLearningService

router = APIRouter(prefix="/campaigns", tags=["campaigns"])

@router.post("/start", response_model=CampaignResponse)
async def start_campaign(request: CampaignBriefRequest, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """Receives brief, creates campaign, and kicks off async orchestration up to approval gate."""
    service = CampaignService(db)
    campaign = service.create_campaign(request)
    
    # Run orchestration in background
    orchestrator = AgentOrchestrator(db)
    background_tasks.add_task(orchestrator.generate_campaign_plan, campaign.id)
    
    return campaign

# ── Historical Learning (must be before /{campaign_id} to avoid path conflicts) ──

@router.get("/learning")
async def get_historical_learnings(db: Session = Depends(get_db)):
    """Returns accumulated learnings from all past campaigns."""
    service = HistoricalLearningService(db)
    learnings = await service.get_learnings()
    return {"learnings": learnings}

# ── Campaign CRUD ──

@router.get("/", response_model=List[CampaignResponse])
def get_campaigns(db: Session = Depends(get_db)):
    return db.query(Campaign).all()

@router.get("/{campaign_id}", response_model=CampaignResponse)
def get_campaign(campaign_id: int, db: Session = Depends(get_db)):
    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return campaign

@router.post("/{campaign_id}/approve")
async def approve_campaign(campaign_id: int, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """Approves humanity-in-the-loop and continues to Execution -> MAB Optimization"""
    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
        
    if campaign.status != "pending_approval":
        raise HTTPException(status_code=400, detail="Campaign not awaiting approval")
        
    orchestrator = AgentOrchestrator(db)
    background_tasks.add_task(orchestrator.execute_and_optimize, campaign.id, max_loops=3)
    
    service = CampaignService(db)
    return service.update_status(campaign_id, "approved")

@router.post("/{campaign_id}/reject")
async def reject_campaign(campaign_id: int, feedback: dict, db: Session = Depends(get_db)):
    """Rejects campaign plan. Optionally handles regenerations."""
    service = CampaignService(db)
    return service.update_status(campaign_id, "draft")

# ── Campaign Metrics & Runs ──

@router.get("/{campaign_id}/metrics", response_model=List[CampaignRunResponse])
def get_campaign_runs(campaign_id: int, db: Session = Depends(get_db)):
    runs = db.query(CampaignRun).filter(CampaignRun.campaign_id == campaign_id).all()
    return runs

# ── Agent Logs ──

@router.get("/{campaign_id}/logs", response_model=List[AgentLogResponse])
def get_agent_logs(campaign_id: int, db: Session = Depends(get_db)):
    query = db.query(AgentLog).filter(AgentLog.campaign_id == campaign_id)
    return query.order_by(AgentLog.timestamp.asc()).all()

# ── Campaign Insights ──

@router.get("/{campaign_id}/insights", response_model=List[CampaignInsightResponse])
def get_campaign_insights(campaign_id: int, db: Session = Depends(get_db)):
    service = InsightService(db)
    return service.get_insights(campaign_id)

# ── Segment Intelligence ──

@router.get("/{campaign_id}/segment-intelligence")
async def get_segment_intelligence(campaign_id: int, db: Session = Depends(get_db)):
    """Returns AI-generated intelligence for each segment in a campaign."""
    service = SegmentIntelligenceService(db)
    intelligence = await service.generate_intelligence(campaign_id)
    return {"intelligence": intelligence}

# ── Optimization Timeline ──

@router.get("/{campaign_id}/optimization-timeline")
def get_optimization_timeline(campaign_id: int, db: Session = Depends(get_db)):
    """
    Returns average open/click rates per optimization run for timeline visualization.
    """
    runs = (
        db.query(CampaignRun)
        .filter(CampaignRun.campaign_id == campaign_id)
        .order_by(CampaignRun.loop_index)
        .all()
    )

    timeline = []
    for run in runs:
        if not run.metrics:
            continue
        avg_open = sum(m.open_rate for m in run.metrics) / len(run.metrics)
        avg_click = sum(m.click_rate for m in run.metrics) / len(run.metrics)

        # Find the best performing variant in this run
        best_metric = max(run.metrics, key=lambda m: m.click_rate)
        
        timeline.append({
            "run_number": run.loop_index,
            "avg_open_rate": round(avg_open, 4),
            "avg_click_rate": round(avg_click, 4),
            "best_variant": f"Variant {best_metric.variant.variant_label}" if best_metric.variant else "N/A",
            "status": run.status,
        })

    return {"timeline": timeline}
