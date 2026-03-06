import asyncio
import logging
import os
from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware

from database import engine, Base, get_db
from api.campaign_api import router as campaign_router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Note: We won't re-create tables here if we use alembic or init_db, but safe to have Base.metadata.create_all
Base.metadata.create_all(bind=engine)

app = FastAPI(title="CampaignX API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, restrict this to the frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(campaign_router)

@app.get("/health")
def health_check():
    return {"status": "ok"}

# Global logs endpoint (used by AgentLogsPage which fetches all logs)
@app.get("/logs")
def get_all_logs(db = Depends(get_db)):
    from models import AgentLog
    from schemas import AgentLogResponse
    logs = db.query(AgentLog).order_by(AgentLog.timestamp.desc()).all()
    return logs

