from sqlalchemy.orm import Session
from models import CampaignRun, PerformanceMetric, Segment, EmailVariant
import datetime
import logging

logger = logging.getLogger(__name__)

class AnalyticsService:
    def __init__(self, db: Session):
        self.db = db
        
    def create_run(self, campaign_id: int, loop_index: int) -> CampaignRun:
        run = CampaignRun(
            campaign_id=campaign_id,
            loop_index=loop_index,
            status="running",
            executed_time=datetime.datetime.utcnow()
        )
        self.db.add(run)
        self.db.commit()
        self.db.refresh(run)
        return run
        
    def save_metrics(self, run_id: int, metrics_data: list):
        # We need segment_id and variant_id to link
        run = self.db.query(CampaignRun).filter(CampaignRun.id == run_id).first()
        if not run:
            return
            
        segments = self.db.query(Segment).filter(Segment.campaign_id == run.campaign_id).all()
        seg_map = {s.name: s.id for s in segments}
        
        for m in metrics_data:
            raw_seg_id = m.get("segment_id") or seg_map.get(m["segment_name"])
            if not raw_seg_id:
                logger.warning(f"No segment found for {m.get('segment_name')} or ID {m.get('segment_id')}")
                continue
                
            try:
                seg_id = int(raw_seg_id)
                variant = self.db.query(EmailVariant).filter(
                    EmailVariant.segment_id == seg_id,
                    EmailVariant.variant_label == m["variant_label"]
                ).first()
                
                if variant:
                    metric = PerformanceMetric(
                        run_id=run_id,
                        segment_id=seg_id,
                        variant_id=variant.id,
                        open_rate=m["open_rate"],
                        click_rate=m["click_rate"]
                    )
                    self.db.add(metric)
                else:
                    logger.warning(f"No variant found for segment {seg_id} with label {m['variant_label']}")
            except (ValueError, TypeError) as e:
                logger.error(f"Error processing metric for segment {raw_seg_id}: {e}")
                
        self.db.commit()
