from sqlalchemy import Column, Integer, String, Float, ForeignKey, Text, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

class Campaign(Base):
    __tablename__ = "campaigns"
    
    id = Column(Integer, primary_key=True, index=True)
    brief = Column(Text, nullable=True)
    product = Column(String, nullable=True)
    constraints = Column(Text, nullable=True)
    target_segments = Column(Text, nullable=True) # JSON string
    tone = Column(String, nullable=True)
    optimization_goal = Column(String, nullable=True)
    cta_url = Column(String, nullable=True)
    status = Column(String, default="draft") # draft, pending_approval, approved, running, completed
    created_at = Column(DateTime, default=datetime.utcnow)
    
    segments = relationship("Segment", back_populates="campaign", cascade="all, delete-orphan")
    runs = relationship("CampaignRun", back_populates="campaign", cascade="all, delete-orphan")
    logs = relationship("AgentLog", back_populates="campaign", cascade="all, delete-orphan")

class Segment(Base):
    __tablename__ = "segments"
    
    id = Column(Integer, primary_key=True, index=True)
    campaign_id = Column(Integer, ForeignKey("campaigns.id"))
    name = Column(String, index=True)
    customer_ids = Column(Text, nullable=True) # JSON string array of IDs
    customer_count = Column(Integer, default=0)
    
    campaign = relationship("Campaign", back_populates="segments")
    variants = relationship("EmailVariant", back_populates="segment", cascade="all, delete-orphan")

class EmailVariant(Base):
    __tablename__ = "email_variants"
    
    id = Column(Integer, primary_key=True, index=True)
    segment_id = Column(Integer, ForeignKey("segments.id"))
    variant_label = Column(String, index=True) # 'A', 'B'
    subject = Column(String)
    body = Column(Text)
    
    segment = relationship("Segment", back_populates="variants")

class CampaignRun(Base):
    __tablename__ = "campaign_runs"
    
    id = Column(Integer, primary_key=True, index=True)
    campaign_id = Column(Integer, ForeignKey("campaigns.id"))
    loop_index = Column(Integer, default=1) # 1, 2, 3
    status = Column(String, default="scheduled")
    api_campaign_id = Column(String, nullable=True)  # External campaign_id from send_campaign API
    scheduled_time = Column(DateTime, nullable=True)
    executed_time = Column(DateTime, nullable=True)
    
    campaign = relationship("Campaign", back_populates="runs")
    metrics = relationship("PerformanceMetric", back_populates="run", cascade="all, delete-orphan")

class PerformanceMetric(Base):
    __tablename__ = "performance_metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    run_id = Column(Integer, ForeignKey("campaign_runs.id"))
    segment_id = Column(Integer, ForeignKey("segments.id"))
    variant_id = Column(Integer, ForeignKey("email_variants.id"))
    open_rate = Column(Float, default=0.0)
    click_rate = Column(Float, default=0.0)
    
    run = relationship("CampaignRun", back_populates="metrics")
    segment = relationship("Segment")
    variant = relationship("EmailVariant")

class AgentLog(Base):
    __tablename__ = "agent_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    campaign_id = Column(Integer, ForeignKey("campaigns.id"), nullable=True)
    agent_name = Column(String, index=True)
    input_data = Column(Text, nullable=True) # JSON string
    output_data = Column(Text, nullable=True) # JSON string
    reasoning_summary = Column(Text, nullable=True)
    api_calls_executed = Column(Text, nullable=True, default="{}") # JSON strictly
    status = Column(String, default="completed")  # 'running', 'completed', 'error'
    action_description = Column(String, nullable=True)  # Short human-readable action text
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    campaign = relationship("Campaign", back_populates="logs")

class CampaignInsight(Base):
    __tablename__ = "campaign_insights"
    
    id = Column(Integer, primary_key=True, index=True)
    campaign_id = Column(Integer, ForeignKey("campaigns.id"))
    segment_name = Column(String, index=True)
    top_segment = Column(String, nullable=True)
    winning_subject_pattern = Column(String, nullable=True)
    best_send_time = Column(String, nullable=True)
    key_insight = Column(Text, nullable=True)
    recommendation = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    campaign = relationship("Campaign", backref="insights")
