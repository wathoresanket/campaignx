"""
StrategyEngine — Determines optimal send times and A/B testing plans per segment.
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List
from engines.base_engine import BaseEngine
from schemas import StrategyOutputSchema

logger = logging.getLogger(__name__)


def _future_send_time(hours_offset: int = 1) -> str:
    """Returns a send time `hours_offset` hours from now in DD:MM:YY HH:MM:SS format (IST)."""
    future = datetime.now() + timedelta(hours=hours_offset)
    return future.strftime("%d:%m:%y %H:%M:%S")


class StrategyEngine(BaseEngine):

    async def run(self, segments: List[Dict[str, Any]], historical_context: str = "") -> List[Dict[str, Any]]:
        """
        Determines optimal send times and A/B testing plans for all segments.
        Uses a single LLM call for efficiency.
        """

        history = self._build_history_section(historical_context)

        # Remove customer_ids to keep prompt small
        slim_segments = [
            {k: v for k, v in seg.items() if k != "customer_ids"}
            for seg in segments
        ]

        if not slim_segments:
            return []

        # Compute a dynamic valid scheduling window: now+1hr to now+72hrs
        window_start = datetime.now() + timedelta(hours=1)
        window_end = datetime.now() + timedelta(hours=72)
        window_start_str = window_start.strftime("%d %B %Y %H:%M IST")
        window_end_str = window_end.strftime("%d %B %Y %H:%M IST")

        prompt = f"""
        You are a strategic marketing optimization engine.

        For each customer segment below determine:
        - an optimal send time
        - a brief A/B testing idea for subject lines or messaging tone

        IMPORTANT:
        Campaign MUST be scheduled between {window_start_str} and {window_end_str}.
        Do NOT schedule in the past. All send_time values must be strictly in the future.
        send_time must be in format: DD:MM:YY HH:MM:SS (IST)

        Guidance for choosing send times (IST):
        - Working professionals: weekday 08:00–09:30 or 19:00–21:00
        - Senior citizens: weekday 10:00–12:00
        - General audience: 10:00–12:00 or 18:00–20:00
        - Avoid midnight and early-morning slots

        Segments:
        {json.dumps(slim_segments, indent=2)}

        {history}

        Return a JSON ARRAY where each object has:
        - "segment_name": string
        - "description": string (the exact same description provided in input)
        - "send_time": string in DD:MM:YY HH:MM:SS format
        - "variants_count": integer (always 2)
        - "ab_testing_plan": short description
        """

        try:
            parsed_output = await self._complete_pydantic(
                prompt,
                List[StrategyOutputSchema],
                temperature=0.2
            )

            results = []
            matched_names = set()
            for strategy in parsed_output:
                result = strategy.model_dump()
                result["variants_count"] = 2  # enforce rule
                # Safety guard: if LLM returns a past timestamp, replace with +2hr from now
                result["send_time"] = self._validate_send_time(result.get("send_time"))
                results.append(result)
                matched_names.add(result["segment_name"])

            # Guarantee every input segment has a strategy
            for i, seg in enumerate(slim_segments):
                name = seg.get("name")
                if name not in matched_names:
                    logger.warning(f"StrategyEngine: Injecting fallback strategy for missed segment: {name}")
                    results.append({
                        "segment_name": name,
                        "description": seg.get("description", ""),
                        "send_time": _future_send_time(hours_offset=2 + i),
                        "variants_count": 2,
                        "ab_testing_plan": "Default A/B performance test — subject line curiosity vs benefit-first"
                    })

            return results

        except Exception as e:
            logger.error(f"StrategyEngine failed: {e}")

            # Safe fallback — all times are guaranteed future
            fallback = []
            for i, seg in enumerate(slim_segments):
                fallback.append({
                    "segment_name": seg.get("name", "Unknown"),
                    "description": seg.get("description", ""),
                    "send_time": _future_send_time(hours_offset=1 + i),
                    "variants_count": 2,
                    "ab_testing_plan": "Default A/B subject line test"
                })

            return fallback

    @staticmethod
    def _validate_send_time(send_time_str: str) -> str:
        """
        Parses the LLM-returned send_time and ensures it is in the future.
        If it cannot be parsed or is in the past, returns now+2hr as a safe default.
        """
        if not send_time_str:
            return _future_send_time(hours_offset=2)

        for fmt in ("%d:%m:%y %H:%M:%S", "%d-%m-%y %H:%M:%S", "%d/%m/%y %H:%M:%S"):
            try:
                dt = datetime.strptime(send_time_str, fmt)
                if dt > datetime.now():
                    # Valid future time — reformat to canonical format just in case
                    return dt.strftime("%d:%m:%y %H:%M:%S")
                else:
                    logger.warning(
                        f"StrategyEngine._validate_send_time: '{send_time_str}' is in the past. "
                        f"Replacing with now+2hr."
                    )
                    return _future_send_time(hours_offset=2)
            except ValueError:
                continue

        logger.warning(
            f"StrategyEngine._validate_send_time: Could not parse '{send_time_str}'. "
            f"Replacing with now+2hr."
        )
        return _future_send_time(hours_offset=2)