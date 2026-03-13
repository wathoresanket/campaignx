"""
CampaignCoordinator
───────────────────
Coordinates the multi-engine campaign pipeline:
  Plan phase:  Brief → Segmentation → Strategy → Content → Approval Gate
  Run phase:   Execution → Analytics → Optimization (loop) → Insights

All customer data and campaign execution flows through the real CampaignX API.
The database serves as a memory layer for internal state and history.
"""

import os
import json
import logging
import asyncio
from sqlalchemy.orm import Session

from models import Campaign, CampaignRun, Segment
from schemas import CampaignBriefRequest
from custom_logging.agent_logger import log_system_action
from config import settings
from tools.openapi_loader import OpenAPILoader
from tools.dynamic_tool_registry import DynamicToolRegistry

from engines.brief_processor import BriefProcessor
from engines.segment_engine import SegmentEngine
from engines.strategy_engine import StrategyEngine
from engines.content_engine import ContentEngine
from engines.execution_engine import ExecutionEngine
from engines.analytics_engine import AnalyticsEngine
from engines.optimization_engine import OptimizationEngine
from engines.insight_engine import InsightEngine

from services.campaign_service import CampaignService
from services.analytics_service import AnalyticsService
from services.optimization_service import OptimizationService
from services.insight_service import InsightService
from services.historical_learning_service import HistoricalLearningService

logger = logging.getLogger(__name__)


# ── Helpers ────────────────────────────────────────────────────────────

def _log(db, module_name, campaign_id, input_data, output_data,
         logic, status, action, external_calls=None):
    """Thin wrapper around log_system_action to reduce call-site verbosity."""
    log_system_action(
        db, module_name, campaign_id, input_data, output_data,
        logic, external_calls=external_calls, status=status, action_description=action,
    )


class CampaignCoordinator:
    """Runs the full campaign pipeline with progressive logging."""

    def __init__(self, db: Session):
        self.db = db

        # Services
        self.campaign_svc = CampaignService(db)
        self.analytics_svc = AnalyticsService(db)
        self.optimization_svc = OptimizationService(db)
        self.insight_svc = InsightService(db)
        self.learning_svc = HistoricalLearningService(db)

        # Dynamic API discovery: load OpenAPI spec → register tools
        spec_path = os.path.join(os.path.dirname(__file__), "..", "tools", "openapi.json")
        loader = OpenAPILoader(spec_path)
        tools, routes = loader.extract_tools()
        self.tool_registry = DynamicToolRegistry(
            base_url=settings.CAMPAIGNX_BASE_URL,
            api_key=settings.CAMPAIGNX_API_KEY,
        )
        for tool in tools:
            op_id = tool["function"]["name"]
            route = routes[op_id]
            self.tool_registry.register_tool(op_id, route["path"], route["method"])
        logger.info(f"Coordinator discovered {len(tools)} API tools via OpenAPI spec")

        # Engines
        self.brief_processor = BriefProcessor()
        self.segment_engine = SegmentEngine()
        self.strategy_engine = StrategyEngine()
        self.content_engine = ContentEngine()
        self.execution_engine = ExecutionEngine()
        self.analytics_engine = AnalyticsEngine()
        self.optimization_engine = OptimizationEngine()
        self.insight_engine = InsightEngine()

    # ── Plan Phase (up to human approval gate) ─────────────────────

    async def generate_campaign_plan(self, campaign_id: int):
        """Runs Brief → Segmentation → Strategy → Content, then waits for approval."""
        try:
            campaign = self.db.query(Campaign).filter(Campaign.id == campaign_id).first()
            if not campaign:
                raise ValueError("Campaign not found")

            brief_text = campaign.brief
            historical_ctx = self.learning_svc.get_learning_context_string()

            # 1. Parse brief
            parsed_brief = await self._execute_task(
                campaign_id, "BriefProcessor",
                self.brief_processor.run, [brief_text],
                input_data={"brief": brief_text},
                action_running="Processing campaign brief",
                action_done="Processed campaign brief into structured data",
            )
            self.campaign_svc.save_parsed_brief(campaign_id, parsed_brief)

            # 2. Fetch REAL customer cohort via dynamically discovered API tool
            _log(self.db, "DataConnector", campaign_id, {}, {},
                 "Connecting to customer data via dynamic discovery", "running",
                 "Retrieving real customer cohort data")

            cohort_response = await self.tool_registry.execute(
                "get_customer_cohort_api_v1_get_customer_cohort_get", {}
            )
            cohort_data = cohort_response.get("data", [])

            _log(self.db, "DataConnector", campaign_id, {},
                 {"total_customers": len(cohort_data)},
                 f"Retrieved {len(cohort_data)} customers via dynamic connection", "completed",
                 f"Retrieved {len(cohort_data)} customers from API",
                 external_calls={"get_customer_cohort_api_v1_get_customer_cohort_get": {}})

            # 3. Segment customers using REAL cohort data
            segments = await self._execute_task(
                campaign_id, "SegmentEngine",
                self.segment_engine.run, [parsed_brief],
                kwargs={"cohort_data": cohort_data},
                input_data={"parsed_brief": parsed_brief, "cohort_size": len(cohort_data)},
                action_running="Applying micro-segmentation logic",
                action_done="Created customer micro-segments from real cohort data",
            )
            self.campaign_svc.save_segments(campaign_id, segments)

            # 4. Generate strategy (with historical learning)
            strategies = await self._execute_task(
                campaign_id, "StrategyEngine",
                self.strategy_engine.run, [segments],
                kwargs={"historical_context": historical_ctx},
                input_data=segments,
                action_running="Determining optimal delivery strategy",
                action_done="Generated segment strategies with historical learning",
            )

            # 5. Generate email content (with historical learning)
            variants = await self._execute_task(
                campaign_id, "ContentEngine",
                self.content_engine.run, [parsed_brief, strategies],
                kwargs={"historical_context": historical_ctx},
                input_data=strategies,
                action_running="Generating structured email variants",
                action_done="Generated email variants for all segments",
            )
            self.campaign_svc.save_variants(campaign_id, variants)

            self.campaign_svc.update_status(campaign_id, "pending_approval")
            logger.info(f"Campaign {campaign_id} plan generated — awaiting approval.")
            
            if settings.DEMO_MODE:
                logger.info("DEMO_MODE enabled. Finished campaign generation phase rapidly.")
        except Exception as e:
            logger.error(f"Error generating plan for campaign {campaign_id}: {e}")
            self.campaign_svc.update_status(campaign_id, "failed")
            _log(self.db, "Coordinator", campaign_id, {}, {"error": str(e)},
                 f"Campaign planning failed: {e}", "error", "Campaign plan generation failed")

    # ── Run Phase (execution → optimization loop → insights) ───────

    async def execute_and_optimize(self, campaign_id: int, max_loops: int = 3):
        """Runs execution, analytics, and MAB optimization in a loop, then generates insights."""
        try:
            self.campaign_svc.update_status(campaign_id, "running")

            campaign = self.db.query(Campaign).filter(Campaign.id == campaign_id).first()
            execution_plan, segments_info = self._build_execution_plan(campaign)

            previous_metrics = None

            for loop in range(1, max_loops + 1):
                logger.info(f"Campaign {campaign_id} — optimization loop {loop}/{max_loops}")
                run = self.analytics_svc.create_run(campaign_id, loop)

                # 5. Execute campaign via REAL send_campaign API
                exec_result = await self._execute_task(
                    campaign_id, "ExecutionEngine",
                    self.execution_engine.run, [execution_plan],
                    kwargs={"segments_with_ids": segments_info},
                    input_data=execution_plan,
                    action_running=f"Executing campaign delivery via API (loop {loop})",
                    action_done=f"Campaign delivered via real API (loop {loop})",
                )

                # Store each api_campaign_id on the run for later report lookup
                sent_campaigns = exec_result.get("sent_campaigns", [])
                api_campaign_ids = [
                    sc["api_campaign_id"] for sc in sent_campaigns
                    if sc.get("api_campaign_id")
                ]
                if api_campaign_ids:
                    run.api_campaign_id = json.dumps(api_campaign_ids)
                    self.db.commit()

                # 6. Collect REAL metrics via get_report API
                metrics = await self._execute_task(
                    campaign_id, "AnalyticsEngine",
                    self.analytics_engine.run, [sent_campaigns],
                    kwargs={"previous_metrics": previous_metrics},
                    action_running=f"Capturing engagement telemetry from API (loop {loop})",
                    action_done=f"Computed performance metrics from real reports (loop {loop})",
                )
                self.analytics_svc.save_metrics(run.id, metrics)

                # 7. Optimize
                opt_decision = await self._execute_task(
                    campaign_id, "OptimizationEngine",
                    self.optimization_engine.run, [metrics],
                    input_data=metrics,
                    action_running=f"Running performance optimization (loop {loop})",
                    action_done=f"Updated strategy via performance results (loop {loop})",
                )
                self.optimization_svc.save_optimization_decisions(run.id, opt_decision)

                if opt_decision.get("stop_optimization") or loop == max_loops:
                    logger.info(f"Optimization complete for campaign {campaign_id} at loop {loop}.")
                    break
                previous_metrics = metrics
                
                if not settings.DEMO_MODE:
                    logger.info(f"Waiting 15 seconds before next optimization loop...")
                    await asyncio.sleep(15)

            # 8. Generate insights from all run data
            all_metrics = self._compile_all_metrics(campaign_id)
            insights = await self._execute_task(
                campaign_id, "InsightEngine",
                self.insight_engine.run, [all_metrics],
                input_data={"raw_metrics": all_metrics},
                action_running="Distilling campaign insights from performance metrics",
                action_done="Generated actionable marketing insights",
            )
            self.insight_svc.save_insights_batch(campaign_id, insights)

            self.campaign_svc.update_status(campaign_id, "completed")
            logger.info(f"Campaign {campaign_id} fully executed and optimized.")
        except Exception as e:
            logger.error(f"Error executing/optimizing campaign {campaign_id}: {e}")
            self.campaign_svc.update_status(campaign_id, "failed")
            _log(self.db, "Coordinator", campaign_id, {}, {"error": str(e)},
                 f"Campaign execution sequence failed: {e}", "error", "Campaign execution failed")

    # ── Internal Helpers ───────────────────────────────────────────

    async def _execute_task(self, campaign_id, module_name, fn, args,
                           kwargs=None, input_data=None,
                           action_running="", action_done="", external_calls=None):
        """
        Wraps every engine call with 'running' → execute → 'completed' logging.
        Reduces the 4-line log+call+log+save pattern to a single call.
        """
        _log(self.db, module_name, campaign_id, {}, {},
             f"Starting {module_name} operation", "running", action_running)

        result = await fn(*args, **(kwargs or {}))

        # We can extract external_calls from the engine instance if it exposes them, otherwise default to None
        calls_used = external_calls or getattr(fn.__self__, 'api_calls_executed', None)

        _log(self.db, module_name, campaign_id,
             input_data or {}, result,
             f"Finished {module_name} operation", "completed", action_done, external_calls=calls_used)
        return result

    @staticmethod
    def _build_execution_plan(campaign):
        """
        Builds the execution plan from approved campaign data.
        Returns (execution_plan, segments_info) where:
          - execution_plan: {segment_id: [{label, subject, body}]}
          - segments_info: [{id, name, customer_ids}]
        """
        execution_plan = {}
        segments_info = []

        for seg in campaign.segments:
            execution_plan[str(seg.id)] = [
                {"label": v.variant_label, "subject": v.subject, "body": v.body}
                for v in seg.variants
            ]
            segments_info.append({
                "id": seg.id,
                "segment_id": str(seg.id),
                "name": seg.name,
                "customer_ids": seg.customer_ids,  # JSON string of real customer IDs
                "customer_count": seg.customer_count,
            })

        return execution_plan, segments_info

    def _compile_all_metrics(self, campaign_id: int):
        """Gathers all performance metrics across optimization runs."""
        runs = self.db.query(CampaignRun).filter(
            CampaignRun.campaign_id == campaign_id
        ).all()
        return [
            {
                "loop": run.loop_index,
                "segment_name": m.segment.name,
                "variant": m.variant.variant_label,
                "open_rate": m.open_rate,
                "click_rate": m.click_rate,
            }
            for run in runs for m in run.metrics
        ]

    async def regenerate_campaign_plan(self, campaign_id: int, feedback: str):
        """
        Re-runs the plan phase incorporating human rejection feedback.
        Injects the feedback into Strategy and Content engine prompts
        so the system can generate improved variants.
        """
        try:
            campaign = self.db.query(Campaign).filter(Campaign.id == campaign_id).first()
            if not campaign:
                raise ValueError("Campaign not found")

            self.campaign_svc.update_status(campaign_id, "generating")

            _log(self.db, "Coordinator", campaign_id, {"feedback": feedback}, {},
                 f"Regenerating campaign plan with feedback: {feedback}", "running",
                 "Clearing old plan and re-generating based on feedback")

            # Clear old segments/variants to avoid duplicates
            self.campaign_svc.delete_campaign_content(campaign_id)

            brief_text = campaign.brief
            historical_ctx = self.learning_svc.get_learning_context_string()

            # Add rejection feedback to historical context
            feedback_context = (
                f"\n\nFEEDBACK (previous plan was rejected):\n{feedback}\n"
                f"Please address this feedback in the new plan."
            )
            enriched_ctx = historical_ctx + feedback_context

            # Re-parse brief (same as original)
            parsed_brief = await self._execute_task(
                campaign_id, "BriefProcessor",
                self.brief_processor.run, [brief_text],
                input_data={"brief": brief_text, "regeneration": True},
                action_running="Re-processing campaign brief",
                action_done="Re-processed campaign brief",
            )
            self.campaign_svc.save_parsed_brief(campaign_id, parsed_brief)

            # Fetch cohort again via dynamic connection
            cohort_response = await self.tool_registry.execute(
                "get_customer_cohort_api_v1_get_customer_cohort_get", {}
            )
            cohort_data = cohort_response.get("data", [])
            _log(self.db, "DataConnector", campaign_id, {}, {"total_customers": len(cohort_data)},
                 "Re-fetched customer data", "completed", "Re-fetched cohort",
                 external_calls={"get_customer_cohort_api_v1_get_customer_cohort_get": {}})

            # Re-segment
            segments = await self._execute_task(
                campaign_id, "SegmentEngine",
                self.segment_engine.run, [parsed_brief],
                kwargs={"cohort_data": cohort_data},
                input_data={"parsed_brief": parsed_brief, "cohort_size": len(cohort_data)},
                action_running="Re-applying micro-segmentation with feedback",
                action_done="Re-created segments incorporating feedback",
            )
            self.campaign_svc.save_segments(campaign_id, segments)

            # Re-generate strategy (with feedback injected)
            strategies = await self._execute_task(
                campaign_id, "StrategyEngine",
                self.strategy_engine.run, [segments],
                kwargs={"historical_context": enriched_ctx},
                input_data=segments,
                action_running="Regenerating strategy with feedback",
                action_done="Generated improved strategy based on feedback",
            )

            # Re-generate content (with feedback injected)
            variants = await self._execute_task(
                campaign_id, "ContentEngine",
                self.content_engine.run, [parsed_brief, strategies],
                kwargs={"historical_context": enriched_ctx},
                input_data=strategies,
                action_running="Regenerating email variants based on feedback",
                action_done="Generated improved email variants",
            )
            self.campaign_svc.save_variants(campaign_id, variants)

            # Update status back to pending_approval
            self.campaign_svc.update_status(campaign_id, "pending_approval")

            _log(self.db, "Coordinator", campaign_id,
                 {"feedback": feedback}, {"variants_count": len(variants)},
                 "Campaign plan regenerated successfully", "completed",
                 "Regeneration complete — awaiting re-approval")
        except Exception as e:
            logger.error(f"Error regenerating plan for campaign {campaign_id}: {e}")
            self.campaign_svc.update_status(campaign_id, "failed")
            _log(self.db, "Coordinator", campaign_id, {}, {"error": str(e)},
                 f"Campaign regeneration failed: {e}", "error", "Campaign plan regeneration failed")

