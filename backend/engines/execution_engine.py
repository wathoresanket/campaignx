"""
ExecutionEngine
───────────────
Dispatches campaigns via dynamically discovered API tools from the OpenAPI spec.
Uses OpenAPILoader to discover the send_campaign endpoint at runtime,
then dispatches through the DynamicToolRegistry.
"""

import json
import logging
import os
import random
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, List

from engines.base_engine import BaseEngine
from config import settings
from tools.openapi_loader import OpenAPILoader
from tools.dynamic_tool_registry import DynamicToolRegistry

logger = logging.getLogger(__name__)

# Path to the OpenAPI spec file
SPEC_PATH = os.path.join(os.path.dirname(__file__), "..", "tools", "openapi.json")


class ExecutionEngine(BaseEngine):
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

        logger.info(f"ExecutionEngine discovered {len(tools)} API tools: {self.registry.get_registered_tools()}")

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
                name = seg.get("name", "unknown")
                if isinstance(customer_ids, str):
                    try:
                        customer_ids = json.loads(customer_ids)
                    except (json.JSONDecodeError, TypeError):
                        customer_ids = []
                segments_map[seg_id] = {"customers": customer_ids, "name": name}

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
            if settings.DEMO_MODE:
                import uuid
                # Simulation: Wait a moment to mimic real API latency
                await asyncio.sleep(0.5)
                result = {
                    "campaign_id": str(uuid.uuid4()),
                    "message": "SIMULATED: Campaign sent successfully via Demo Mode",
                    "status": "success"
                }
                logger.info(f"DEMO_MODE: Simulated dispatch for variant {variant.get('label')}")
            else:
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
                "segment_name": variant.get("segment_name", "unknown"),
                "variant_label": variant.get("label", ""),
                "api_campaign_id": api_campaign_id,
                "send_time": send_time,
                "customer_count": len(customer_ids),
                "api_response": result.get("message", ""),
            }

        tasks = []
        for seg_id, variants in execution_plan.items():
            seg_data = segments_map.get(seg_id, {})
            all_customer_ids = seg_data.get("customers", [])
            seg_name = seg_data.get("name", "unknown")

            if not all_customer_ids:
                logger.warning(f"No customer_ids for segment {seg_id}, skipping")
                continue

            # Sub-sample 70% of customers randomly so each loop has fresh data
            # This prevents flat metrics from re-emailing the exact same people
            sample_size = max(1, int(len(all_customer_ids) * 0.7))
            customer_ids = random.sample(all_customer_ids, min(sample_size, len(all_customer_ids)))
            logger.info(
                f"Segment {seg_id}: sampling {len(customer_ids)}/{len(all_customer_ids)} customers"
            )

            for variant in variants:
                v_copy = variant.copy()
                v_copy["segment_name"] = seg_name
                tasks.append(_dispatch_variant(v_copy, seg_id, customer_ids))

        if tasks:
            sent_campaigns = await asyncio.gather(*tasks)

        # Record dynamically executed tools for logging
        self.api_calls_executed = {"send_campaign_api_v1_send_campaign_post": {
            "invocations": len(sent_campaigns),
            "endpoint": "/api/v1/send_campaign"
        }}

        return {"sent_campaigns": list(sent_campaigns)}

    @staticmethod
    def _default_send_time() -> str:
        """Generate a default send time 1 hour from now in DD:MM:YY HH:MM:SS format (IST)."""
        future = datetime.now() + timedelta(hours=1)
        return future.strftime("%d:%m:%y %H:%M:%S")