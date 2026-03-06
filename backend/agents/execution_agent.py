"""
ExecutionAgent
───────────────
Dispatches campaigns via the real CampaignX send_campaign API.
Each segment+variant combination is sent as a separate API call.
Returns the API-assigned campaign_ids for later report retrieval.
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List

from agents.base_agent import BaseAgent
from tools.campaignx_api_client import CampaignXAPIClient

logger = logging.getLogger(__name__)


class ExecutionAgent(BaseAgent):
    """Sends campaigns via the real CampaignX API and tracks campaign_ids."""

    def __init__(self):
        super().__init__()
        self.api_client = CampaignXAPIClient()

    async def run(
        self,
        execution_plan: Dict[str, Any],
        segments_with_ids: List[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Sends each segment+variant combination via the real API.

        Args:
            execution_plan: Dict mapping segment_id -> list of variant dicts
                            with keys: label, subject, body, send_time
            segments_with_ids: List of segment dicts with customer_ids for dispatch

        Returns:
            Dict with sent_campaigns (list of dispatch results with api_campaign_id)
        """
        sent_campaigns = []
        segments_map = {}

        # Build lookup: segment_id -> customer_ids
        if segments_with_ids:
            for seg in segments_with_ids:
                seg_id = str(seg.get("id", seg.get("segment_id", "")))
                customer_ids = seg.get("customer_ids", [])
                if isinstance(customer_ids, str):
                    try:
                        customer_ids = json.loads(customer_ids)
                    except (json.JSONDecodeError, TypeError):
                        customer_ids = []
                segments_map[seg_id] = customer_ids

        for seg_id, variants in execution_plan.items():
            customer_ids = segments_map.get(seg_id, [])
            if not customer_ids:
                logger.warning(f"No customer_ids for segment {seg_id}, skipping")
                continue

            for variant in variants:
                subject = variant.get("subject", "Campaign Email")
                body = variant.get("body", "")
                send_time = variant.get("send_time", self._default_send_time())

                logger.info(
                    f"Dispatching variant {variant.get('label', '?')} "
                    f"to {len(customer_ids)} customers in segment {seg_id}"
                )

                result = await self.api_client.send_campaign(
                    subject=subject,
                    body=body,
                    customer_ids=customer_ids,
                    send_time=send_time,
                )

                api_campaign_id = result.get("campaign_id")
                sent_campaigns.append({
                    "segment_id": seg_id,
                    "variant_label": variant.get("label", ""),
                    "api_campaign_id": api_campaign_id,
                    "send_time": send_time,
                    "customer_count": len(customer_ids),
                    "api_response": result.get("message", ""),
                })

                if api_campaign_id:
                    logger.info(f"  → API campaign_id: {api_campaign_id}")
                else:
                    logger.error(f"  → Send failed: {result}")

        return {"sent_campaigns": sent_campaigns}

    @staticmethod
    def _default_send_time() -> str:
        """Generate a default send time 1 hour from now in DD:MM:YY HH:MM:SS format."""
        future = datetime.now() + timedelta(hours=1)
        return future.strftime("%d:%m:%y %H:%M:%S")
