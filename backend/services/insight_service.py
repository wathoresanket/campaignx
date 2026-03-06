from sqlalchemy.orm import Session
from models import CampaignInsight
from typing import List

class InsightService:
    def __init__(self, db: Session):
        self.db = db

    def save_insight(self, campaign_id: int, segment_name: str, insight_content: str) -> CampaignInsight:
        insight = CampaignInsight(
            campaign_id=campaign_id,
            segment_name=segment_name,
            insight_content=insight_content
        )
        self.db.add(insight)
        self.db.commit()
        self.db.refresh(insight)
        return insight

    def save_insights_batch(self, campaign_id: int, insights_data: List[dict]):
        for item in insights_data:
            insight = CampaignInsight(
                campaign_id=campaign_id,
                segment_name=item.get("segment_name", "Unknown"),
                insight_content=item.get("insight_content", "")
            )
            self.db.add(insight)
        self.db.commit()

    def get_insights(self, campaign_id: int) -> List[CampaignInsight]:
        return self.db.query(CampaignInsight).filter(CampaignInsight.campaign_id == campaign_id).order_by(CampaignInsight.timestamp.desc()).all()
