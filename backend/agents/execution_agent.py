"""
ExecutionAgent
───────────────
Dispatches campaigns via dynamically discovered API tools from the OpenAPI spec.
Uses OpenAPILoader to discover the send_campaign endpoint at runtime,
then dispatches through the DynamicToolRegistry.
"""

import json
import logging
import os
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, List

from agents.base_agent import BaseAgent
from config import settings
from tools.openapi_loader import OpenAPILoader
from tools.dynamic_tool_registry import DynamicToolRegistry

logger = logging.getLogger(__name__)

# Path to the OpenAPI spec file
SPEC_PATH = os.path.join(os.path.dirname(__file__), "..", "tools", "openapi.json")


class ExecutionAgent(BaseAgent):
    """
    Sends campaigns via dynamically discovered API tools.
    Loads the OpenAPI spec at init → discovers send_campaign endpoint →
    dispatches through DynamicToolRegistry.
    """

    def __init__(self):
        super().__init__()
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

        logger.info(f"ExecutionAgent discovered {len(tools)} API tools: {self.registry.get_registered_tools()}")

    async def run(
        self,
        execution_plan: Dict[str, Any],
        segments_with_ids: List[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Sends each segment+variant combination via dynamically discovered API.

        Args:
            execution_plan: Dict mapping segment_id → list of variant dicts
                            with keys: label, subject, body, send_time
            segments_with_ids: List of segment dicts with customer_ids for dispatch
        """
        sent_campaigns = []
        segments_map = {}

        # Build lookup: segment_id → customer_ids
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

        async def _dispatch_variant(variant: Dict[str, Any], seg_id: str, customer_ids: List[str]):
            subject = variant.get("subject", "Campaign Email")
            body = variant.get("body", "")
            send_time = variant.get("send_time", self._default_send_time())

            logger.info(
                f"Dispatching variant {variant.get('label', '?')} "
                f"to {len(customer_ids)} customers in segment {seg_id} "
                f"via dynamically discovered send_campaign tool"
            )

            # Execute via dynamic tool registry (discovered from OpenAPI spec)
            result = await self.registry.execute(
                "send_campaign_api_v1_send_campaign_post",
                {
                    "subject": subject,
                    "body": body,
                    "list_customer_ids": customer_ids,
                    "send_time": send_time,
                },
            )

            api_campaign_id = result.get("campaign_id")
            if api_campaign_id:
                logger.info(f"  → API campaign_id: {api_campaign_id}")
            else:
                logger.error(f"  → Send failed: {result}")

            return {
                "segment_id": seg_id,
                "variant_label": variant.get("label", ""),
                "api_campaign_id": api_campaign_id,
                "send_time": send_time,
                "customer_count": len(customer_ids),
                "api_response": result.get("message", ""),
            }

        tasks = []
        for seg_id, variants in execution_plan.items():
            customer_ids = segments_map.get(seg_id, [])
            if not customer_ids:
                logger.warning(f"No customer_ids for segment {seg_id}, skipping")
                continue

            for variant in variants:
                tasks.append(_dispatch_variant(variant, seg_id, customer_ids))

        if tasks:
            sent_campaigns = await asyncio.gather(*tasks)

        # Record dynamically executed tools for logging
        self.api_calls_executed = {"send_campaign_api_v1_send_campaign_post": {
            "invocations": len(sent_campaigns),
            "endpoint": "/api/v1/send_campaign"
        }}

        return {"sent_campaigns": sent_campaigns}

    @staticmethod
    def _default_send_time() -> str:
        """Generate a default send time 1 hour from now in DD:MM:YY HH:MM:SS format (IST)."""
        future = datetime.now() + timedelta(hours=1)
        return future.strftime("%d:%m:%y %H:%M:%S")
