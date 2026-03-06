from sqlalchemy.orm import Session
from models import CampaignInsight
from typing import List

class InsightService:
    def __init__(self, db: Session):
        self.db = db

    def save_insights_batch(self, campaign_id: int, insights_data: List[dict]):
        for item in insights_data:
            insight = CampaignInsight(
                campaign_id=campaign_id,
                segment_name=item.get("segment_name", "Unknown"),
                top_segment=item.get("top_segment", ""),
                winning_subject_pattern=item.get("winning_subject_pattern", ""),
                best_send_time=item.get("best_send_time", ""),
                key_insight=item.get("key_insight", ""),
                recommendation=item.get("recommendation", "")
            )
            self.db.add(insight)
        self.db.commit()

    def get_insights(self, campaign_id: int) -> List[CampaignInsight]:
        return self.db.query(CampaignInsight).filter(CampaignInsight.campaign_id == campaign_id).order_by(CampaignInsight.timestamp.desc()).all()
