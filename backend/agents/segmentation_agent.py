"""
SegmentationAgent
──────────────────
Segments customers into micro-groups based on the parsed brief and
real customer cohort data from the CampaignX API.

Uses a two-step approach:
1. Defines segment rules from the campaign brief (fast — small prompt)
2. Python applies rules to full cohort (instant — pure computation)
"""

import json
import logging
from typing import Dict, Any, List

from agents.base_agent import BaseAgent

logger = logging.getLogger(__name__)


class SegmentationAgent(BaseAgent):
    """Defines segment rules from the brief, then applies them to the full cohort."""

    async def run(
        self,
        parsed_brief: Dict[str, Any],
        cohort_data: List[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Two-step segmentation:
        1. Define segment rules based on cohort summary (fast)
        2. Apply rules programmatically to assign all customers (instant)
        """
        customers = cohort_data or []
        cohort_summary = self._summarize_cohort(customers)

        # Step 1: Define segment RULES (not assign individual customers)
        prompt = f"""
        You are an advanced customer segmentation expert. 
        Based on the campaign brief and customer cohort summary below, define 4-6 highly specific micro-segment RULES.

        Instead of broad groups, build micro-segments combining factors like:
        - age group
        - gender
        - investment profile
        - engagement history
        
        Examples of good micro-segments: "young professionals", "senior citizens", "female senior citizens", "inactive high-net-worth customers".
        
        CRITICAL INSTRUCTION:
        For each rule, you must provide a valid Python boolean expression string in the `condition` field.
        The expression will be evaluated against a dictionary variable `c` representing one customer.
        Use c.get('FieldName', default) syntax. Examples:
        - Age filter: "c.get('Age', 0) >= 60"
        - Gender filter: "c.get('Gender', '') == 'Male'"
        - Combined: "c.get('Age', 0) >= 60 and c.get('Gender', '') == 'Female'"
        - Income: "c.get('Monthly_Income', 0) > 200000"
        For the catch_all segment, set condition to "True" and catch_all to true.
        
        Campaign Brief:
        {json.dumps(parsed_brief, indent=2)}

        Customer Cohort Summary:
        {cohort_summary}
        """
        try:
            from schemas import SegmentationRulesSchema
            result = await self._complete_pydantic(prompt, SegmentationRulesSchema)
            segment_rules = [rule.model_dump() for rule in result.segments]
            logger.info(f"Defined {len(segment_rules)} segment rules")

            # Step 2: Apply rules to assign all customers (instant)
            segments = self._apply_rules(segment_rules, customers)
            logger.info(f"Created {len(segments)} segments from {len(customers)} customers")
            return segments
        except Exception as e:
            logger.error(f"SegmentationAgent failed: {e}")
            raise

    def _apply_rules(
        self,
        rules: List[Dict[str, Any]],
        customers: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """Applies segment rules to assign all customers."""
        assigned = set()
        segments = []
        catch_all_rule = None

        # First pass: apply non-catch-all rules
        for rule in rules:
            if rule.get("catch_all"):
                catch_all_rule = rule
                continue

            condition_str = rule.get("condition", "True")
            name = rule.get("name", "Segment")
            logger.info(f"Evaluating rule '{name}' with condition: {condition_str}")

            matching_ids = []
            eval_errors = 0
            for c in customers:
                cid = c.get("customer_id", "")
                if cid in assigned:
                    continue
                try:
                    if eval(condition_str, {"__builtins__": {}}, {"c": c}):
                        matching_ids.append(cid)
                        assigned.add(cid)
                except Exception:
                    eval_errors += 1

            if eval_errors > 0:
                logger.warning(f"Rule '{name}': {eval_errors} eval errors out of {len(customers)} customers")
            logger.info(f"Rule '{name}': matched {len(matching_ids)} customers")

            if matching_ids:
                segments.append({
                    "name": name,
                    "customer_count": len(matching_ids),
                    "customer_ids": matching_ids,
                })

        # Second pass: catch-all for remaining customers
        remaining_ids = [
            c.get("customer_id", "") for c in customers
            if c.get("customer_id", "") not in assigned
        ]
        if remaining_ids:
            catch_all_name = catch_all_rule.get("name", "General Audience") if catch_all_rule else "General Audience"
            segments.append({
                "name": catch_all_name,
                "customer_count": len(remaining_ids),
                "customer_ids": remaining_ids,
            })

        return segments

    @staticmethod
    def _summarize_cohort(cohort_data: List[Dict[str, Any]]) -> str:
        """
        Builds a compact statistical summary for the segmentation prompt.
        Does NOT include individual customer IDs — just distributions.
        """
        if not cohort_data:
            return "No cohort data available."

        total = len(cohort_data)

        # Collect all available fields from first record
        sample_fields = list(cohort_data[0].keys()) if cohort_data else []

        # Build distribution for categorical fields
        distributions: Dict[str, Dict[str, int]] = {}
        categorical_fields = ["Occupation", "Gender", "Marital_Status", "City",
                              "KYC status", "App_Installed", "Existing Customer",
                              "Social_Media_Active", "Occupation type"]

        for field in categorical_fields:
            if field not in sample_fields:
                continue
            dist: Dict[str, int] = {}
            for c in cohort_data:
                val = str(c.get(field, "Unknown"))
                dist[val] = dist.get(val, 0) + 1
            # Only include top 10 values
            top = sorted(dist.items(), key=lambda x: -x[1])[:10]
            distributions[field] = dict(top)

        # Age stats if available
        age_stats = ""
        if "Age" in sample_fields:
            ages = [c.get("Age", 0) for c in cohort_data if c.get("Age")]
            if ages:
                age_stats = f"\nAge: min={min(ages)}, max={max(ages)}, avg={sum(ages)/len(ages):.0f}"

        dist_lines = []
        for field, dist in distributions.items():
            entries = [f"    {v}: {count} ({count*100/total:.1f}%)" for v, count in dist.items()]
            dist_lines.append(f"  {field}:\n" + "\n".join(entries))

        summary = f"""Total customers: {total}
Available fields: {', '.join(sample_fields)}{age_stats}

Distributions:
{chr(10).join(dist_lines)}

Sample Records (first 3):
{json.dumps(cohort_data[:3], indent=2)}
"""
        return summary
