import json
from sqlalchemy.orm import Session
from models import Campaign, Segment, EmailVariant
from schemas import CampaignBriefRequest

class CampaignService:
    def __init__(self, db: Session):
        self.db = db

    def create_campaign(self, request: CampaignBriefRequest) -> Campaign:
        db_campaign = Campaign(brief=request.brief, status="generating")
        self.db.add(db_campaign)
        self.db.commit()
        self.db.refresh(db_campaign)
        return db_campaign
        
    def save_parsed_brief(self, campaign_id: int, parsed_data: dict):
        campaign = self.db.query(Campaign).filter(Campaign.id == campaign_id).first()
        if campaign:
            campaign.product = parsed_data.get("product")
            campaign.constraints = parsed_data.get("constraints")
            campaign.target_segments = json.dumps(parsed_data.get("target_segments", []))
            campaign.tone = parsed_data.get("tone")
            campaign.optimization_goal = parsed_data.get("optimization_goal")
            campaign.cta_url = parsed_data.get("cta_url")
            self.db.commit()
            
    def save_segments(self, campaign_id: int, segments_data: list):
        for seg in segments_data:
            segment = Segment(
                campaign_id=campaign_id,
                name=seg.get("name"),
                customer_count=seg.get("customer_count"),
                customer_ids=str(seg.get("customers", []))
            )
            self.db.add(segment)
        self.db.commit()

    def save_variants(self, campaign_id: int, content_data: dict):
        segments = self.db.query(Segment).filter(Segment.campaign_id == campaign_id).all()
        seg_map = {s.name: s.id for s in segments}
        
        for seg_name, variants in content_data.items():
            seg_id = seg_map.get(seg_name)
            if seg_id:
                for v in variants:
                    variant = EmailVariant(
                        segment_id=seg_id,
                        variant_label=v.get("label"),
                        subject=v.get("subject"),
                        body=v.get("body")
                    )
                    self.db.add(variant)
        self.db.commit()

    def update_status(self, campaign_id: int, status: str):
        campaign = self.db.query(Campaign).filter(Campaign.id == campaign_id).first()
        if campaign:
            campaign.status = status
            self.db.commit()
            return campaign
        return None
