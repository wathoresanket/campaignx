"""
OptimizationEngine — Multi-Armed Bandit optimizer for campaign performance.
"""

import json
import logging
from typing import Dict, Any, List
from engines.base_engine import BaseEngine

logger = logging.getLogger(__name__)


class OptimizationEngine(BaseEngine):

    async def run(self, curr_metrics: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyzes current run metrics using MAB principles.
        Returns optimization decisions for the next loop.
        """
        # Strip any large nested data from metrics before analysis
        slim_metrics = []
        for m in curr_metrics:
            slim_metrics.append({
                k: v for k, v in m.items()
                if k not in ("customer_ids", "report_data", "raw_data")
            })

        prompt = f"""
        You are a performance optimization engine for email marketing using Multi-Armed Bandit (MAB) principles.
        Analyze these metrics and decide the next action per segment: exploit the winning variant (~70%) or explore (~30%).
        
        CRITICAL RULE:
        Evaluate variant performance using the primary scoring criterion: total count of 'Email Clicked' (EC=Y) and 'Email Opened' (EO=Y).
        Formula for performance score: Score = (0.7 * click_rate) + (0.3 * open_rate).

        Current Run Metrics:
        {json.dumps(slim_metrics, indent=2)}

        Decide the best variant based on the weighted score, and generate adjustments for the losing variants (send time, subject style, emoji usage) in order to explore better options.
        If the best click rate is > 15%, set stop_optimization to true.
        """
        try:
            from schemas import OptimizationDecisionSchema
            result = await self._complete_pydantic(prompt, OptimizationDecisionSchema)
            return result.model_dump()
        except Exception as e:
            logger.error(f"OptimizationAgent failed: {e}")
            raise
