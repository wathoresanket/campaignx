"""
SegmentationAgent
──────────────────
Segments customers into micro-groups based on the parsed brief and
real customer cohort data from the CampaignX API.
"""

import json
import logging
from typing import Dict, Any, List

from agents.base_agent import BaseAgent

logger = logging.getLogger(__name__)


class SegmentationAgent(BaseAgent):
    """Uses LLM to cluster real customer cohort data into marketing segments."""

    async def run(
        self,
        parsed_brief: Dict[str, Any],
        cohort_data: List[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Segments customers based on parsed brief and real cohort data.

        Args:
            parsed_brief: Structured campaign brief from CampaignBriefAgent.
            cohort_data: Real customer list from get_customer_cohort API.
                         Each customer has: customer_id, Email_ID, FirstName,
                         LastName, Occupation, etc.

        Returns:
            List of segment dicts with name, customer_count, customer_ids.
        """
        cohort_summary = self._summarize_cohort(cohort_data or [])

        prompt = f"""
        You are a customer segmentation expert. Based on the campaign brief and 
        the REAL customer cohort data below, create 2-4 meaningful micro-segments.

        Campaign Brief:
        {json.dumps(parsed_brief, indent=2)}

        Customer Cohort Summary:
        {cohort_summary}

        Total Customers Available: {len(cohort_data or [])}

        IMPORTANT: Create segments based on the ACTUAL customer attributes you see
        in the cohort data (e.g., Occupation, demographics). Assign real customer_ids
        to each segment.

        Output a JSON object with key "segments" containing a list of objects:
        - "name": string (descriptive segment name based on real attributes)
        - "customer_count": integer (actual count of customers in this segment)
        - "customer_ids": list of strings (actual customer_id values from the cohort)

        Ensure every customer is assigned to exactly one segment.
        """
        try:
            result = await self._complete_json(prompt)
            segments = result.get("segments", [])
            logger.info(f"Created {len(segments)} segments from {len(cohort_data or [])} customers")
            return segments
        except Exception as e:
            logger.error(f"SegmentationAgent failed: {e}")
            raise

    @staticmethod
    def _summarize_cohort(cohort_data: List[Dict[str, Any]]) -> str:
        """
        Builds a statistical summary of the real cohort data for the LLM prompt.
        Includes occupation distribution and a sample of customer records.
        """
        if not cohort_data:
            return "No cohort data available."

        total = len(cohort_data)

        # Occupation distribution
        occupations: Dict[str, int] = {}
        for c in cohort_data:
            occ = c.get("Occupation", "Unknown")
            occupations[occ] = occupations.get(occ, 0) + 1

        occ_lines = [f"  - {occ}: {count} ({count*100/total:.1f}%)"
                     for occ, count in sorted(occupations.items(), key=lambda x: -x[1])]

        # Collect all available fields from the first record
        sample_fields = list(cohort_data[0].keys()) if cohort_data else []

        # Sample records (first 5 for context, but send all customer_ids separately)
        sample_records = cohort_data[:5]

        summary = f"""Total customers: {total}
Available fields: {', '.join(sample_fields)}

Occupation Distribution:
{chr(10).join(occ_lines)}

Sample Records (first 5):
{json.dumps(sample_records, indent=2)}

All Customer IDs:
{json.dumps([c.get('customer_id', '') for c in cohort_data])}
"""
        return summary
