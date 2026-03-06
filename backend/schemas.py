from pydantic import BaseModel, Field
from typing import List, Optional, Any
from datetime import datetime

# Common
class ORMBase(BaseModel):
    model_config = {"from_attributes": True}

# Campaign Brief Request
class CampaignBriefRequest(BaseModel):
    brief: str

# Email Variant
class EmailVariantBase(BaseModel):
    variant_label: str
    subject: str
    body: str

class EmailVariantResponse(EmailVariantBase, ORMBase):
    id: int
    segment_id: int

# Segment
class SegmentBase(BaseModel):
    name: str
    customer_count: int

class SegmentResponse(SegmentBase, ORMBase):
    id: int
    campaign_id: int
    customer_ids: Optional[Any] = None # Or string if returning JSON
    variants: List[EmailVariantResponse] = []

# Campaign
class CampaignBase(BaseModel):
    brief: Optional[str] = None
    product: Optional[str] = None
    constraints: Optional[str] = None
    target_segments: Optional[str] = None
    tone: Optional[str] = None
    optimization_goal: Optional[str] = None
    cta_url: Optional[str] = None
    status: Optional[str] = "draft"

class CampaignResponse(CampaignBase, ORMBase):
    id: int
    created_at: datetime
    segments: List[SegmentResponse] = []

# Performance Metrics
class PerformanceMetricResponse(BaseModel):
    id: int
    run_id: int
    segment_id: int
    variant_id: int
    open_rate: float
    click_rate: float
    class Config:
        from_attributes = True

# Campaign Run
class CampaignRunResponse(BaseModel):
    id: int
    campaign_id: int
    loop_index: int
    status: str
    api_campaign_id: Optional[str] = None
    scheduled_time: Optional[datetime]
    executed_time: Optional[datetime]
    metrics: List[PerformanceMetricResponse] = []
    class Config:
        from_attributes = True

# Agent Log
class AgentLogResponse(BaseModel):
    id: int
    campaign_id: Optional[int]
    agent_name: str
    input_data: Optional[str]
    output_data: Optional[str]
    reasoning_summary: Optional[str]
    status: Optional[str] = "completed"  # 'running', 'completed', 'error'
    action_description: Optional[str] = None  # Short human-readable action text
    timestamp: Optional[datetime] = None
    class Config:
        from_attributes = True

# Campaign Insight
class CampaignInsightResponse(BaseModel):
    id: int
    campaign_id: int
    segment_name: str
    insight_content: str
    timestamp: datetime
    class Config:
        from_attributes = True
