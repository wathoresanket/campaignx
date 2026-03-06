import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import engine, Base
# Import all models so they get registered with SQLAlchemy
from models import Campaign, Segment, EmailVariant, CampaignRun, PerformanceMetric, AgentLog

def init_db():
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully!")

if __name__ == "__main__":
    init_db()
