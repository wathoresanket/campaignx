"""
ContentAgent — Generates A/B email variants per segment.
"""

import json
import logging
from typing import Dict, Any, List
from agents.base_agent import BaseAgent

logger = logging.getLogger(__name__)


class ContentAgent(BaseAgent):

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

        prompt = f"""
        You are an expert copywriter. Generate 2 email variants (A and B) for each segment.
        
        Campaign Brief Details:
        - Product: {parsed_brief.get('product')}
        - Tone: {parsed_brief.get('tone')}
        - Constraints: {parsed_brief.get('constraints')}
        - CTA URL: {parsed_brief.get('cta_url', 'https://superbfsi.com/xdeposit/explore/')}

        Strategies per segment:
        {json.dumps(strategies, indent=2)}
        {history}
        Rules:
        - Write only in English.
        - Include the CTA URL if provided.
        - Variant A should be standard/professional.
        - Variant B should use emojis, be concise, and try a different formatting.
        - Ensure constraints (e.g. extra 0.25% for female senior citizens) apply only to the relevant segment.

        Output JSON format:
        {{
            "content": [
                {{
                    "segment_name": "...",
                    "variants": [
                        {{"label": "A", "subject": "...", "body": "..."}},
                        {{"label": "B", "subject": "...", "body": "..."}}
                    ]
                }}
            ]
        }}
        """
        try:
            result = await self._complete_json(prompt)
            content = result.get("content", [])
            # Convert list → dict keyed by segment_name
            return {item["segment_name"]: item["variants"] for item in content}
        except Exception as e:
            logger.error(f"ContentAgent failed: {e}")
            raise

    def _mock_response(self, strategies: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, str]]]:
        result = {}
        for strategy in strategies:
            seg_name = strategy["segment_name"]
            subject_a = f"Exclusive XDeposit offer for {seg_name.replace('_', ' ').title()}"
            body_a = "Hello,\n\nWe are pleased to offer you an exclusive return on XDeposit. Visit https://superbfsi.com/xdeposit/explore/ to learn more.\n\nBest,\nSuperBFSI Team"
            subject_b = "🚀 Boost your wealth with XDeposit!"
            body_b = "Hey!\n\nReady to earn more? Check out the new XDeposit features! 🔥\n\nTap here: https://superbfsi.com/xdeposit/explore/\n\nCheers,\nSuperBFSI"

            if "female_senior" in seg_name.lower():
                body_a = "Hello,\n\nAs a valued female senior citizen, you get an extra 0.25% returns on XDeposit. Visit https://superbfsi.com/xdeposit/explore/ to learn more.\n\nBest,\nSuperBFSI Team"
                body_b = "Hey!\n\nYou're eligible for an EXTRA 0.25% return on XDeposit! 💰👵\n\nTap here: https://superbfsi.com/xdeposit/explore/\n\nCheers,\nSuperBFSI"

            result[seg_name] = [
                {"label": "A", "subject": subject_a, "body": body_a},
                {"label": "B", "subject": subject_b, "body": body_b},
            ]
        return result
