from sqlalchemy.orm import Session
from models import CampaignRun

class OptimizationService:
    def __init__(self, db: Session):
        self.db = db
        
    def save_optimization_decisions(self, run_id: int, decisions: dict):
        # In a more complex schema, we would save these explicitly to an 'optimizations' table.
        # For now, we can log them or update the run status.
        run = self.db.query(CampaignRun).filter(CampaignRun.id == run_id).first()
        if run:
            # We just update that this run finished and spawned an optimization cycle
            run.status = "completed"
            self.db.commit()
