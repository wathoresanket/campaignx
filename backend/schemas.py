from pydantic import BaseModel
from typing import List, Optional, Any
from datetime import datetime

# Common base class for ORM models
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
    description: Optional[str] = None

class SegmentResponse(SegmentBase, ORMBase):
    id: int
    campaign_id: int
    customer_ids: Optional[Any] = None
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
    key_benefits: Optional[Any] = None
    special_conditions: Optional[str] = None
    status: Optional[str] = "draft"

class CampaignResponse(CampaignBase, ORMBase):
    id: int
    created_at: datetime
    segments: List[SegmentResponse] = []

# Performance Metrics
class PerformanceMetricResponse(ORMBase):
    id: int
    run_id: int
    segment_id: int
    variant_id: int
    open_rate: float
    click_rate: float

# Campaign Run
class CampaignRunResponse(ORMBase):
    id: int
    campaign_id: int
    loop_index: int
    status: str
    api_campaign_id: Optional[str] = None
    scheduled_time: Optional[datetime]
    executed_time: Optional[datetime]
    metrics: List[PerformanceMetricResponse] = []

# System Log
class SystemLogResponse(ORMBase):
    id: int
    campaign_id: Optional[int]
    module_name: str
    input_data: Optional[str]
    output_data: Optional[str]
    logic_summary: Optional[str]
    external_calls: Optional[str] = "{}"
    status: Optional[str] = "completed"
    action_description: Optional[str] = None
    timestamp: Optional[datetime] = None

# Campaign Insight
class CampaignInsightBase(BaseModel):
    segment_name: str
    top_segment: str
    winning_subject_pattern: str
    best_send_time: str
    key_insight: str
    recommendation: str

class CampaignInsightResponse(CampaignInsightBase, ORMBase):
    id: int
    campaign_id: int
    timestamp: datetime

# Agent Output Schemas (Structured Validation)
class BriefOutputSchema(BaseModel):
    product: str
    constraints: str
    target_segments: List[str]
    tone: str
    optimization_goal: str
    cta_url: Optional[str] = None
    key_benefits: List[str] = []
    global_benefits: List[str] = []
    conditional_benefits: List[str] = []
    special_conditions: Optional[str] = None

class SegmentRuleSchema(BaseModel):
    name: str
    description: str
    condition: str
    catch_all: bool

class SegmentationRulesSchema(BaseModel):
    segments: List[SegmentRuleSchema]

class StrategyOutputSchema(BaseModel):
    segment_name: str
    description: str
    send_time: str
    variants_count: int
    ab_testing_plan: str

class StrategiesOutputSchema(BaseModel):
    strategies: List[StrategyOutputSchema]
    
class VariantContentSchema(BaseModel):
    label: str
    subject: str
    body: str

class ContentVariantsSchema(BaseModel):
    segment_name: str
    variants: List[VariantContentSchema]
    
class OptimizationDecisionItemSchema(BaseModel):
    segment_name: str
    best_variant: str
    highest_click_rate: float
    action: str
    send_time_adjustment: str
    subject_style: str
    emoji_usage: str

class OptimizationDecisionSchema(BaseModel):
    decisions: List[OptimizationDecisionItemSchema]
    stop_optimization: bool

class InsightItemSchema(BaseModel):
    segment_name: str
    top_segment: str
    winning_subject_pattern: str
    best_send_time: str
    key_insight: str
    recommendation: str

class InsightsOutputSchema(BaseModel):
    insights: List[InsightItemSchema]


# Modular Content Generation Schemas
class SubjectLinesSchema(BaseModel):
    subjects: List[str]


class EmailBodiesSchema(BaseModel):
    bodies: List[str]


class VariantScoreSchema(BaseModel):
    label: str
    score: int

class VariantScoresSchema(BaseModel):
    scores: List[VariantScoreSchema]
