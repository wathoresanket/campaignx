"""
AnalyticsAgent
───────────────
Fetches real campaign performance reports via dynamically discovered API tools.
Uses OpenAPILoader to discover the get_report endpoint at runtime,
then fetches through the DynamicToolRegistry.
Computes open_rate and click_rate from raw EO/EC flags.
"""

import os
import logging
from typing import Dict, Any, List

from config import settings
from tools.openapi_loader import OpenAPILoader
from tools.dynamic_tool_registry import DynamicToolRegistry

logger = logging.getLogger(__name__)

# Path to the OpenAPI spec file
SPEC_PATH = os.path.join(os.path.dirname(__file__), "..", "tools", "openapi.json")


class AnalyticsAgent:
    """
    Fetches real reports via dynamically discovered API tools and computes metrics.
    Loads the OpenAPI spec at init → discovers get_report endpoint →
    fetches through DynamicToolRegistry.
    """

    def __init__(self):
        # Dynamic API discovery: load spec → extract tools → register
        self.loader = OpenAPILoader(SPEC_PATH)
        tools, routes = self.loader.extract_tools()
        self.registry = DynamicToolRegistry(
            base_url=settings.CAMPAIGNX_BASE_URL,
            api_key=settings.CAMPAIGNX_API_KEY,
        )
        for tool in tools:
            op_id = tool["function"]["name"]
            route = routes[op_id]
            self.registry.register_tool(op_id, route["path"], route["method"])

        logger.info(f"AnalyticsAgent discovered {len(tools)} API tools: {self.registry.get_registered_tools()}")

    async def run(
        self,
        sent_campaigns: List[Dict[str, Any]],
        previous_metrics: List[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Fetches reports for each sent campaign via dynamically discovered API
        and computes metrics from raw EO/EC flags.
        """
        logger.info(f"Fetching reports for {len(sent_campaigns)} dispatched campaigns via dynamic API discovery...")
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

            # Fetch report via dynamic tool registry (discovered from OpenAPI spec)
            report = await self.registry.execute(
                "get_report_api_v1_get_report_get",
                {"campaign_id": api_campaign_id},
            )
            report_data = report.get("data", [])

            # Compute rates from raw EO/EC flags
            # Formula: open_rate = count(EO="Y") / total_rows
            #          click_rate = count(EC="Y") / total_rows
            rates = self.compute_rates(report_data)

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

    @staticmethod
    def compute_rates(report_data: List[Dict[str, Any]]) -> Dict[str, float]:
        """
        Computes open_rate and click_rate from raw report rows.
        Each row has EO (Email Opened: "Y"/"N") and EC (Email Clicked: "Y"/"N").
        Formula: open_rate = count(EO="Y") / total_rows
                 click_rate = count(EC="Y") / total_rows
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
