"""
CampaignX API Client
─────────────────────
Centralized async HTTP client for the external CampaignX API.
Handles authentication, customer cohort retrieval, campaign dispatch, and report fetching.
"""

import logging
from typing import Dict, Any, List, Optional
import httpx
from config import settings

logger = logging.getLogger(__name__)


class CampaignXAPIClient:
    """Async client for the CampaignX external API."""

    def __init__(self, api_key: str = "", base_url: str = ""):
        self.base_url = base_url or settings.CAMPAIGNX_BASE_URL
        self.api_key = api_key or settings.CAMPAIGNX_API_KEY
        self.headers = {
            "X-API-Key": self.api_key,
            "Content-Type": "application/json",
        }

    def _client(self) -> httpx.AsyncClient:
        return httpx.AsyncClient(
            base_url=self.base_url,
            headers=self.headers,
            timeout=30.0,
        )

    # ── Customer Data ──────────────────────────────────────────────

    async def get_customer_cohort(self) -> List[Dict[str, Any]]:
        """
        GET /api/v1/get_customer_cohort
        Returns list of customer dicts with keys like:
          customer_id, Email_ID, FirstName, LastName, Occupation, ...
        """
        async with self._client() as client:
            try:
                resp = await client.get("/api/v1/get_customer_cohort")
                resp.raise_for_status()
                data = resp.json()
                customers = data.get("data", [])
                logger.info(f"Fetched {len(customers)} customers from cohort API")
                return customers
            except Exception as e:
                logger.error(f"Failed to fetch customer cohort: {e}")
                return []

    # ── Campaign Execution ─────────────────────────────────────────

    async def send_campaign(
        self,
        subject: str,
        body: str,
        customer_ids: List[str],
        send_time: str,
    ) -> Dict[str, Any]:
        """
        POST /api/v1/send_campaign
        Returns dict with campaign_id, response_code, invokation_time, message.
        """
        payload = {
            "subject": subject,
            "body": body,
            "list_customer_ids": customer_ids,
            "send_time": send_time,
        }
        async with self._client() as client:
            try:
                resp = await client.post("/api/v1/send_campaign", json=payload)
                resp.raise_for_status()
                result = resp.json()
                logger.info(f"Campaign sent — API campaign_id: {result.get('campaign_id')}")
                return result
            except Exception as e:
                logger.error(f"Failed to send campaign: {e}")
                return {"error": str(e), "campaign_id": None}

    # ── Reports ────────────────────────────────────────────────────

    async def get_report(self, campaign_id: str) -> Dict[str, Any]:
        """
        GET /api/v1/get_report?campaign_id=...
        Returns dict with data (list of per-customer records with EO/EC flags),
        total_rows, response_code, message.
        """
        async with self._client() as client:
            try:
                resp = await client.get(
                    "/api/v1/get_report",
                    params={"campaign_id": campaign_id},
                )
                resp.raise_for_status()
                result = resp.json()
                logger.info(f"Fetched report for campaign {campaign_id}: {result.get('total_rows', 0)} rows")
                return result
            except Exception as e:
                logger.error(f"Failed to fetch report for {campaign_id}: {e}")
                return {"data": [], "total_rows": 0, "error": str(e)}

    # ── Metric Computation ─────────────────────────────────────────

    @staticmethod
    def compute_rates(report_data: List[Dict[str, Any]]) -> Dict[str, float]:
        """
        Computes open_rate and click_rate from raw report rows.
        Each row has EO (Email Opened: "Y"/"N") and EC (Email Clicked: "Y"/"N").
        """
        if not report_data:
            return {"open_rate": 0.0, "click_rate": 0.0}

        total = len(report_data)
        opened = sum(1 for r in report_data if r.get("EO") == "Y")
        clicked = sum(1 for r in report_data if r.get("EC") == "Y")

        return {
            "open_rate": round(opened / total, 4),
            "click_rate": round(clicked / total, 4),
        }
