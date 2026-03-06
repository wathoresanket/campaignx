"""
AgentOrchestrator
─────────────────
Coordinates the multi-agent campaign pipeline:
  Plan phase:  Brief → Segmentation → Strategy → Content → Approval Gate
  Run phase:   Execution → Analytics → Optimization (loop) → Insights

All customer data and campaign execution flows through the real CampaignX API.
The database serves as a memory layer for internal state and history.
"""

import json
import logging
from sqlalchemy.orm import Session

from models import Campaign, CampaignRun, Segment
from schemas import CampaignBriefRequest
from custom_logging.agent_logger import log_agent_action
from tools.campaignx_api_client import CampaignXAPIClient

from agents.campaign_brief_agent import CampaignBriefAgent
from agents.segmentation_agent import SegmentationAgent
from agents.strategy_agent import StrategyAgent
from agents.content_agent import ContentAgent
from agents.execution_agent import ExecutionAgent
from agents.analytics_agent import AnalyticsAgent
from agents.optimization_agent import OptimizationAgent
from agents.insight_agent import InsightAgent

from services.campaign_service import CampaignService
from services.analytics_service import AnalyticsService
from services.optimization_service import OptimizationService
from services.insight_service import InsightService
from services.historical_learning_service import HistoricalLearningService

logger = logging.getLogger(__name__)


# ── Helpers ────────────────────────────────────────────────────────────

def _log(db, agent_name, campaign_id, input_data, output_data,
         reasoning, status, action):
    """Thin wrapper around log_agent_action to reduce call-site verbosity."""
    log_agent_action(
        db, agent_name, campaign_id, input_data, output_data,
        reasoning, status=status, action_description=action,
    )


class AgentOrchestrator:
    """Runs the full campaign pipeline with progressive logging."""

    def __init__(self, db: Session):
        self.db = db

        # Services
        self.campaign_svc = CampaignService(db)
        self.analytics_svc = AnalyticsService(db)
        self.optimization_svc = OptimizationService(db)
        self.insight_svc = InsightService(db)
        self.learning_svc = HistoricalLearningService(db)

        # External API client
        self.api_client = CampaignXAPIClient()

        # Agents
        self.brief_agent = CampaignBriefAgent()
        self.segmentation_agent = SegmentationAgent()
        self.strategy_agent = StrategyAgent()
        self.content_agent = ContentAgent()
        self.execution_agent = ExecutionAgent()
        self.analytics_agent = AnalyticsAgent()
        self.optimization_agent = OptimizationAgent()
        self.insight_agent = InsightAgent()

    # ── Plan Phase (up to human approval gate) ─────────────────────

    async def generate_campaign_plan(self, campaign_id: int):
        """Runs Brief → Segmentation → Strategy → Content, then waits for approval."""
        campaign = self.db.query(Campaign).filter(Campaign.id == campaign_id).first()
        if not campaign:
            raise ValueError("Campaign not found")

        brief_text = campaign.brief
        historical_ctx = self.learning_svc.get_learning_context_string()

        # 1. Parse brief
        parsed_brief = await self._run_agent(
            campaign_id, "CampaignBriefAgent",
            self.brief_agent.run, [brief_text],
            input_data={"brief": brief_text},
            action_running="Parsing campaign brief",
            action_done="Parsed campaign brief into structured data",
        )
        self.campaign_svc.save_parsed_brief(campaign_id, parsed_brief)

        # 2. Fetch REAL customer cohort from API
        _log(self.db, "DataFetcher", campaign_id, {}, {},
             "Fetching customer cohort from CampaignX API", "running",
             "Fetching real customer cohort data")

        cohort_data = await self.api_client.get_customer_cohort()

        _log(self.db, "DataFetcher", campaign_id, {},
             {"total_customers": len(cohort_data)},
             f"Fetched {len(cohort_data)} customers from cohort API", "completed",
             f"Retrieved {len(cohort_data)} customers from API")

        # 3. Segment customers using REAL cohort data
        segments = await self._run_agent(
            campaign_id, "SegmentationAgent",
            self.segmentation_agent.run, [parsed_brief],
            kwargs={"cohort_data": cohort_data},
            input_data={"parsed_brief": parsed_brief, "cohort_size": len(cohort_data)},
            action_running="Creating micro-segments from real customer cohort",
            action_done="Created customer micro-segments from real cohort data",
        )
        self.campaign_svc.save_segments(campaign_id, segments)

        # 4. Generate strategy (with historical learning)
        strategies = await self._run_agent(
            campaign_id, "StrategyAgent",
            self.strategy_agent.run, [segments],
            kwargs={"historical_context": historical_ctx},
            input_data=segments,
            action_running="Selecting optimal send times and A/B test plans",
            action_done="Generated segment strategies with historical learning",
        )

        # 5. Generate email content (with historical learning)
        variants = await self._run_agent(
            campaign_id, "ContentAgent",
            self.content_agent.run, [parsed_brief, strategies],
            kwargs={"historical_context": historical_ctx},
            input_data=strategies,
            action_running="Generating A/B email variants",
            action_done="Generated email variants for all segments",
        )
        self.campaign_svc.save_variants(campaign_id, variants)

        self.campaign_svc.update_status(campaign_id, "pending_approval")
        logger.info(f"Campaign {campaign_id} plan generated — awaiting approval.")

    # ── Run Phase (execution → optimization loop → insights) ───────

    async def execute_and_optimize(self, campaign_id: int, max_loops: int = 3):
        """Runs execution, analytics, and MAB optimization in a loop, then generates insights."""
        self.campaign_svc.update_status(campaign_id, "running")

        campaign = self.db.query(Campaign).filter(Campaign.id == campaign_id).first()
        execution_plan, segments_info = self._build_execution_plan(campaign)

        previous_metrics = None

        for loop in range(1, max_loops + 1):
            logger.info(f"Campaign {campaign_id} — optimization loop {loop}/{max_loops}")
            run = self.analytics_svc.create_run(campaign_id, loop)

            # 5. Execute campaign via REAL send_campaign API
            exec_result = await self._run_agent(
                campaign_id, "ExecutionAgent",
                self.execution_agent.run, [execution_plan],
                kwargs={"segments_with_ids": segments_info},
                input_data=execution_plan,
                action_running=f"Dispatching campaign emails via API (loop {loop})",
                action_done=f"Campaign dispatched via real API (loop {loop})",
            )

            # Store each api_campaign_id on the run for later report lookup
            sent_campaigns = exec_result.get("sent_campaigns", [])
            api_campaign_ids = [
                sc["api_campaign_id"] for sc in sent_campaigns
                if sc.get("api_campaign_id")
            ]
            if api_campaign_ids:
                run.api_campaign_id = json.dumps(api_campaign_ids)
                self.db.commit()

            # 6. Collect REAL metrics via get_report API
            metrics = await self._run_agent(
                campaign_id, "AnalyticsAgent",
                self.analytics_agent.run, [sent_campaigns],
                kwargs={"previous_metrics": previous_metrics},
                action_running=f"Fetching real engagement reports from API (loop {loop})",
                action_done=f"Computed open/click rates from real reports (loop {loop})",
            )
            self.analytics_svc.save_metrics(run.id, metrics)

            # 7. Optimize
            opt_decision = await self._run_agent(
                campaign_id, "OptimizationAgent",
                self.optimization_agent.run, [metrics],
                input_data=metrics,
                action_running=f"Running MAB optimization (loop {loop})",
                action_done=f"Updated strategy via MAB results (loop {loop})",
            )
            self.optimization_svc.save_optimization_decisions(run.id, opt_decision)

            if opt_decision.get("stop_optimization") or loop == max_loops:
                logger.info(f"Optimization complete for campaign {campaign_id} at loop {loop}.")
                break
            previous_metrics = metrics

        # 8. Generate insights from all run data
        all_metrics = self._compile_all_metrics(campaign_id)
        insights = await self._run_agent(
            campaign_id, "InsightAgent",
            self.insight_agent.run, [all_metrics],
            input_data={"raw_metrics": all_metrics},
            action_running="Generating campaign insights from real metrics",
            action_done="Generated actionable marketing insights",
        )
        self.insight_svc.save_insights_batch(campaign_id, insights)

        self.campaign_svc.update_status(campaign_id, "completed")
        logger.info(f"Campaign {campaign_id} fully executed and optimized.")

    # ── Internal Helpers ───────────────────────────────────────────

    async def _run_agent(self, campaign_id, agent_name, fn, args,
                         kwargs=None, input_data=None,
                         action_running="", action_done=""):
        """
        Wraps every agent call with 'running' → execute → 'completed' logging.
        Reduces the 4-line log+call+log+save pattern to a single call.
        """
        _log(self.db, agent_name, campaign_id, {}, {},
             f"Starting {agent_name}", "running", action_running)

        result = await fn(*args, **(kwargs or {}))

        _log(self.db, agent_name, campaign_id,
             input_data or {}, result,
             f"Finished {agent_name}", "completed", action_done)
        return result

    @staticmethod
    def _build_execution_plan(campaign):
        """
        Builds the execution plan from approved campaign data.
        Returns (execution_plan, segments_info) where:
          - execution_plan: {segment_id: [{label, subject, body}]}
          - segments_info: [{id, name, customer_ids}]
        """
        execution_plan = {}
        segments_info = []

        for seg in campaign.segments:
            execution_plan[str(seg.id)] = [
                {"label": v.variant_label, "subject": v.subject, "body": v.body}
                for v in seg.variants
            ]
            segments_info.append({
                "id": seg.id,
                "segment_id": str(seg.id),
                "name": seg.name,
                "customer_ids": seg.customer_ids,  # JSON string of real customer IDs
                "customer_count": seg.customer_count,
            })

        return execution_plan, segments_info

    def _compile_all_metrics(self, campaign_id: int):
        """Gathers all performance metrics across optimization runs."""
        runs = self.db.query(CampaignRun).filter(
            CampaignRun.campaign_id == campaign_id
        ).all()
        return [
            {
                "loop": run.loop_index,
                "segment_name": m.segment.name,
                "variant": m.variant.variant_label,
                "open_rate": m.open_rate,
                "click_rate": m.click_rate,
            }
            for run in runs for m in run.metrics
        ]
