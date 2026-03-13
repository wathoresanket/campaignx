"""
ContentEngine — Generates A/B email variants per segment.
"""

import json
import logging
import asyncio
from typing import Dict, Any, List
from engines.base_engine import BaseEngine

logger = logging.getLogger(__name__)


class ContentEngine(BaseEngine):

    async def run(
        self,
        parsed_brief: Dict[str, Any],
        strategies: List[Dict[str, Any]],
        historical_context: str = "",
    ) -> Dict[str, List[Dict[str, str]]]:
        """
        Generates two email variants (A and B) per segment.
        Optionally uses historical campaign learnings to improve content quality.
        Returns dict mapping segment_name → list of variants.
        """
        history = self._build_history_section(historical_context)

        async def _generate_for_segment(strategy: Dict[str, Any]) -> Dict[str, Any]:
            segment_name = strategy.get("segment_name", "Unknown")
            prompt = f"""
            You are a performance-driven content generation engine. Generate at least 3 email variants (A, B, and C) for the following segment.
            
            Campaign Brief Details:
            - Product: {parsed_brief.get('product', 'XDeposit Term Deposit')}
            - Tone: {parsed_brief.get('tone')}
            - Constraints: {parsed_brief.get('constraints')}
            - CTA URL: {parsed_brief.get('cta_url', 'https://superbfsi.com/xdeposit/explore/')}

            Segment Strategy:
            {json.dumps(strategy, indent=2)}
            {history}
            
            SUPERBFSI "XDEPOSIT" CONTENT RULES (Only if product is XDeposit):
            - The product "XDeposit" offers **1 percentage point higher returns** than competitors.
            - Female senior ciudadanos qualify for an **additional 0.25 percentage point** higher returns (Total 1.25% bonus).
            - Always include the official CTA URL: https://superbfsi.com/xdeposit/explore/
            
            GENERAL CONTENT RULES (For other products):
            - Highlight benefits specific to the product mentioned in the brief.
            - Use the CTA URL provided in the brief (default to a generic SuperBFSI landing page if missing).
            
            Subject Line Optimization Rules:
            Generate multiple subject variations using patterns such as:
            - curiosity gap
            - urgency
            - numbers/statistics
            - personalization tokens
            - benefit-first phrasing
            - emoji variation
            - question format
            
            Example Subject Line patterns:
            "Earn 1% Higher Returns on Your Savings Today"
            "Senior Citizens: Unlock Higher Returns Now"
            "Is Your Money Working Hard Enough?"
            "💰 Earn More on Your Deposits — Limited Time"

            Content Optimization Rules:
            The body generator must:
            - highlight the benefit within the first sentence
            - keep total length between 80-150 words
            - include a single strong CTA
            - place CTA link in two locations
            - emphasize key benefits using **bold formatting**
            - optionally include emoji for engagement
            
            Generate at least 3 variants.
            """
            try:
                from schemas import ContentVariantsSchema
                result = await self._complete_pydantic(prompt, ContentVariantsSchema)
                # Convert the Pydantic object back into a dictionary for downstream compatibility
                return result.model_dump()
            except Exception as e:
                logger.error(f"ContentAgent failed for segment {segment_name}: {e}")
                return {"segment_name": segment_name, "variants": []}

        tasks = [_generate_for_segment(strategy) for strategy in strategies]
        results = await asyncio.gather(*tasks) if tasks else []
        
        # Convert list of results to a dict keyed by segment_name
        return {item["segment_name"]: item.get("variants", []) for item in results}
