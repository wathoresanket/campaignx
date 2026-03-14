import logging
from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import engine, Base
from api.campaign_api import router as campaign_router

logging.basicConfig(level=logging.INFO)

# Create all database tables on startup
try:
    Base.metadata.create_all(bind=engine)
except Exception as e:
    logging.warning(f"Database initialization warning (likely tables exist): {e}")

app = FastAPI(title="CampaignX API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(campaign_router)


@app.get("/health")
def health_check():
    return {"status": "ok"}
