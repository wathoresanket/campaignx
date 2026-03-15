"""
SegmentationAgent
──────────────────
Creates micro-segment RULES from the campaign brief.
Python then applies those rules to the entire cohort.
No hardcoded demographic logic.
"""

import json
import logging
from typing import Dict, Any, List, Optional

from engines.base_engine import BaseEngine

logger = logging.getLogger(__name__)


class SegmentEngine(BaseEngine):

    async def run(
        self,
        parsed_brief: Dict[str, Any],
        cohort_data: List[Dict[str, Any]] = None,
        feedback: Optional[str] = None
    ) -> List[Dict[str, Any]]:

        customers = cohort_data or []
        cohort_summary = self._summarize_cohort(customers)

        prompt = f"""
You are an advanced CRM segmentation engine.

Your task is to DEFINE micro-segment RULES.
Do NOT assign customers yourself — Python will apply the rules.

Segments should combine attributes like:
- demographics
- engagement
- financial behaviour
- lifecycle stage

CRITICAL REQUIREMENTS:

1. EXACT MATCH: You MUST explicitly create one segment for EACH audience listed in the `target_segments` array of the Campaign Brief. The segment `name` MUST exactly, word-for-word, match the string from `target_segments` (e.g., if the brief says "salaried professionals", your segment name MUST be "salaried professionals").

2. RELEVANT SUB-SEGMENTS: In addition to the exact target audience, you MUST create AT LEAST 3 other highly relevant sub-segments that make logical sense for the campaign's product and tone. Do NOT generate random or irrelevant demographic segments. They must be logical extensions of the target market (e.g. if the product is an FD, target high-balance customers).

3. CONDITIONAL BENEFITS: If the campaign brief specifies conditional benefits for certain groups (e.g., senior citizens, specific genders), you MUST ensure those segments are explicitly created so that the Content Engine can tailor emails to them.

4. CATCH-ALL: Always include one final `catch_all: true` segment (e.g., "General Audience" or "All Customers") for anyone who doesn't match the prior rules.

5. Provide a valid Python boolean expression in `condition` that works securely inside an `eval()` call. The customer dictionary is `c`. Make sure you use the EXACT field names from the Customer Cohort Summary!

6. For `catch_all`, you MUST provide a strict JSON boolean (true or false, NO QUOTES). Total segments MUST be at least 4.

Examples:
c.get('Age',0) >= 60
c.get('Gender','') == 'Female'
c.get('Age',0) >= 60 and c.get('Gender','') == 'Female'
c.get('City','') == 'Mumbai'

Campaign Brief:
{json.dumps(parsed_brief, indent=2)}

Customer Cohort Summary:
{cohort_summary}

{f"REJECTION FEEDBACK TO ADDRESS:\n{feedback}" if feedback else ""}

Return segments as a JSON object with a single key `segments` containing the array of rule objects.
"""

        from schemas import SegmentationRulesSchema

        result = await self._complete_pydantic(prompt, SegmentationRulesSchema)
        segment_rules = [rule.model_dump() for rule in result.segments]

        logger.info(f"Defined {len(segment_rules)} segmentation rules")

        segments = self._apply_rules(segment_rules, customers)

        logger.info(
            f"Created {len(segments)} segments from {len(customers)} customers (including empty ones for visibility)"
        )

        return segments


    def _apply_rules(self, rules, customers):
        assigned = set()
        segments = []
        catch_all_rule = None
        
        # Broad keywords that imply a catch-all/general audience
        BROAD_KEYWORDS = {"all customers", "general audience", "everyone", "all"}

        # 1. Separately identify catch_all to ensure it runs last
        # Also treat rules with broad names as catch-alls to prevent specific segment starvation
        priority_rules = []
        for rule in rules:
            name_lower = rule.get("name", "").lower()
            if rule.get("catch_all") or name_lower in BROAD_KEYWORDS:
                # If we encounter multiple catch-all-like rules, keep the one actually marked catch_all
                if not catch_all_rule or rule.get("catch_all"):
                    catch_all_rule = rule
            else:
                priority_rules.append(rule)

        # 2. Process priority rules first
        for rule in priority_rules:
            condition = rule.get("condition", "True")
            name = rule.get("name", "Segment")
            matches = []

            for c in customers:
                cid = c.get("customer_id")
                if cid in assigned:
                    continue

                try:
                    if eval(condition, {"__builtins__": {}}, {"c": c}):
                        matches.append(cid)
                        assigned.add(cid)
                except Exception as eval_err:
                    logger.warning(f"Failed to evaluate condition '{condition}' for cid={cid}: {eval_err}")
                    continue

            # Always append the segment, even if matches is empty, for visibility
            segments.append({
                "name": name,
                "customer_count": len(matches),
                "customer_ids": matches
            })

        # 3. Process catch_all or remaining customers
        remaining = [
            c["customer_id"]
            for c in customers
            if c["customer_id"] not in assigned
        ]

        # Use LLM-provided name for catch-all if available, else default
        catch_all_name = catch_all_rule.get("name", "General Audience") if catch_all_rule else "General Audience"
        
        segments.append({
            "name": catch_all_name,
            "customer_count": len(remaining),
            "customer_ids": remaining
        })

        return segments


    @staticmethod
    def _summarize_cohort(cohort_data):

        if not cohort_data:
            return "No cohort data available."

        total = len(cohort_data)

        sample_fields = list(cohort_data[0].keys())

        distributions = {}

        for field in sample_fields:

            dist = {}

            for c in cohort_data:

                val = str(c.get(field,"Unknown"))

                dist[val] = dist.get(val,0)+1

            if len(dist) <= 20:

                distributions[field] = dist

        return f"""
Total customers: {total}

Fields:
{', '.join(sample_fields)}

Distributions:
{json.dumps(distributions, indent=2)}

Sample records:
{json.dumps(cohort_data[:3], indent=2)}
"""
