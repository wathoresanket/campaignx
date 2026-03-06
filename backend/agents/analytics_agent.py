"""
AnalyticsAgent
───────────────
Fetches real campaign performance reports from the CampaignX API.
Computes open_rate and click_rate from raw EO (Email Opened) / EC (Email Clicked) flags.
"""

import logging
from typing import Dict, Any, List

from tools.campaignx_api_client import CampaignXAPIClient

logger = logging.getLogger(__name__)


class AnalyticsAgent:
    """Fetches real reports and computes metrics — no LLM needed."""

    def __init__(self):
        self.api_client = CampaignXAPIClient()

    async def run(
        self,
        sent_campaigns: List[Dict[str, Any]],
        previous_metrics: List[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Fetches reports for each sent campaign and computes metrics.

        Args:
            sent_campaigns: List of dicts from ExecutionAgent, each with:
                api_campaign_id, segment_id/name, variant_label
            previous_metrics: Optional metrics from previous loop (unused currently)

        Returns:
            List of metric dicts per segment+variant:
              segment_name, variant_label, open_rate, click_rate, total_sent, etc.
        """
        logger.info(f"Fetching reports for {len(sent_campaigns)} dispatched campaigns...")
        results = []

        for campaign in sent_campaigns:
            api_campaign_id = campaign.get("api_campaign_id")
            segment_name = campaign.get("segment_name", campaign.get("segment_id", "unknown"))
            variant_label = campaign.get("variant_label", "?")

            if not api_campaign_id:
                logger.warning(f"No api_campaign_id for {segment_name}/{variant_label}, skipping report")
                results.append({
                    "segment_name": str(segment_name),
                    "variant_label": variant_label,
                    "open_rate": 0.0,
                    "click_rate": 0.0,
                    "total_sent": 0,
                    "total_opened": 0,
                    "total_clicked": 0,
                    "api_campaign_id": None,
                })
                continue

            # Fetch the real report from the API
            report = await self.api_client.get_report(api_campaign_id)
            report_data = report.get("data", [])

            # Compute rates from raw EO/EC flags
            rates = CampaignXAPIClient.compute_rates(report_data)

            total_sent = len(report_data)
            total_opened = sum(1 for r in report_data if r.get("EO") == "Y")
            total_clicked = sum(1 for r in report_data if r.get("EC") == "Y")

            logger.info(
                f"  {segment_name}/{variant_label}: "
                f"open={rates['open_rate']:.2%}, click={rates['click_rate']:.2%} "
                f"({total_sent} sent)"
            )

            results.append({
                "segment_name": str(segment_name),
                "variant_label": variant_label,
                "open_rate": rates["open_rate"],
                "click_rate": rates["click_rate"],
                "total_sent": total_sent,
                "total_opened": total_opened,
                "total_clicked": total_clicked,
                "api_campaign_id": api_campaign_id,
            })

        return results
