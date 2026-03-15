"""
ContentEngine — Generates and optimizes email variants per segment.

Architecture:
Subjects → Bodies → Combine → Score → Select Best

Key Features:
- Segment-aware benefit filtering
- Subject/body independent generation
- Variant recombination
- AI scoring for optimization
"""

import json
import logging
import asyncio
import re
from typing import Dict, Any, List

from engines.base_engine import BaseEngine
from schemas import SubjectLinesSchema, EmailBodiesSchema, VariantScoresSchema

logger = logging.getLogger(__name__)


class ContentEngine(BaseEngine):

    async def run(
        self,
        parsed_brief: Dict[str, Any],
        strategies: List[Dict[str, Any]],
        historical_context: str = "",
    ) -> Dict[str, List[Dict[str, str]]]:

        history = self._build_history_section(historical_context)

        results = []
        # Process sequentially with a small delay to prevent 429 rate limit backoffs
        for strategy in strategies:
            logger.info(f"Generating content for segment: {strategy.get('segment_name')}")
            res = await self._generate_for_segment(parsed_brief, strategy, history)
            results.append(res)
            await asyncio.sleep(1.5)  # Allow API token buckets to refill

        return {item["segment_name"]: item["variants"] for item in results}


    def _get_eligible_benefits(self, segment_name: str, conditional_benefits: List[str]) -> tuple:
        """Pre-filter conditional benefits into eligible and ineligible for this segment."""
        name_lower = segment_name.lower()
        demographic_map = {
            "senior": ["senior", "citizen", "elderly", "retired", "60+"],
            "female": ["female", "woman", "women", "lady", "ladies"],
            "male": ["male", "man", "men", "gentleman", "gentlemen"],
            "youth": ["youth", "student", "young", "college", "under-25", "teen"],
            "professional": ["professional", "salaried", "corporate", "working"],
            "inactive": ["inactive", "dormant", "re-activate"]
        }

        eligible = []
        ineligible = []
        for benefit in conditional_benefits:
            benefit_lower = benefit.lower()
            
            # Find which demographic GROUPS are REQUIRED by this benefit
            required_groups = []
            for group, keywords in demographic_map.items():
                if any(kw in benefit_lower for kw in keywords):
                    required_groups.append(group)
            
            if not required_groups:
                # If no specific demographic mentioned, it shouldn't really be a conditional benefit, 
                # but we'll treat it as eligible to be safe.
                eligible.append(benefit)
                continue

            # Segment MUST satisfy ALL mentioned groups in the benefit
            is_match = True
            for group in required_groups:
                keywords = demographic_map[group]
                if not any(kw in name_lower for kw in keywords):
                    is_match = False
                    break
            
            if is_match:
                eligible.append(benefit)
            else:
                ineligible.append(benefit)
                
        return eligible, ineligible


    async def _generate_for_segment(
        self,
        parsed_brief: Dict[str, Any],
        strategy: Dict[str, Any],
        history: str
    ) -> Dict[str, Any]:

        segment_name = strategy.get("segment_name", "Unknown")
        conditional_benefits = parsed_brief.get("conditional_benefits", [])
        eligible_benefits, ineligible_benefits = self._get_eligible_benefits(segment_name, conditional_benefits)

        try:
            # Parallelize subject and body generation
            subjects_task = self._generate_subjects(parsed_brief, strategy, eligible_benefits)
            bodies_task = self._generate_bodies(parsed_brief, strategy, history, eligible_benefits, ineligible_benefits)

            subjects, bodies = await asyncio.gather(subjects_task, bodies_task)

            variants = self._combine_variants(subjects, bodies)

            # Post-validation: strip any conditional benefits the LLM may have still included for ineligible segments
            global_benefits = parsed_brief.get("global_benefits", parsed_brief.get("key_benefits", []))
            for v in variants:
                v["body"] = self._validate_segment_benefits(segment_name, v["body"], conditional_benefits, global_benefits)

            scored_variants = await self._score_variants(segment_name, variants)

            sorted_variants = sorted(
                scored_variants,
                key=lambda x: x.get("score", 0),
                reverse=True
            )
 
            best = []
            seen_subjects = set()
            for v in sorted_variants:
                if v["subject"] not in seen_subjects:
                    best.append(v)
                    seen_subjects.add(v["subject"])
                if len(best) == 2:
                    break
                    
            # Fallback if we somehow didn't get 2 unique subjects
            if len(best) < 2 and len(sorted_variants) >= 2:
                best.append([x for x in sorted_variants if x not in best][0])
 
            for i, v in enumerate(best):
                v.pop("score", None)
                v["label"] = f"Variant {chr(65 + i)}"

            logger.info(
                f"ContentEngine reasoning: Generated {len(subjects)} subjects × {len(bodies)} bodies "
                f"= {len(variants)} candidates for '{segment_name}'. Top 2 selected."
            )

            return {
                "segment_name": segment_name,
                "variants": best
            }

        except Exception as e:
            logger.error(f"ContentEngine failed for {segment_name}: {e}")

            return {
                "segment_name": segment_name,
                "variants": self._fallback_variants(parsed_brief)
            }


    async def _generate_subjects(self, parsed_brief, strategy, eligible_benefits):

        segment_name = strategy.get("segment_name", "Unknown")
        segment_desc = strategy.get("description", "")

        prompt = f"""
You are an expert email marketing copywriter.

Generate 5 high-performing email subject lines for a SPECIFIC customer segment.

Rules:
- English text only
- 40–65 characters
- No emojis
- Must increase open rate
- STRICT MINDFULNESS OF NUMBERS: You must NOT hallucinate financial claims. Do not invent things like "2.50%" or "0.25%" or "1.50%" unless exactly specified below.
- ABSOLUTELY NO META-COMMENTARY: NEVER write phrases like "this offer is not applicable to you", or acknowledge the existence of other segments or rules. If a benefit doesn't apply, simply DO NOT MENTION IT AT ALL.
- TAILOR subject lines to the segment profile described below.

Campaign:
{parsed_brief.get('product', 'our product')}

Target Segment: {segment_name}
Segment Profile: {segment_desc}

Global Benefits (apply to ALL segments):
{parsed_brief.get("global_benefits", parsed_brief.get("key_benefits", []))}

Eligible Conditional Benefits for THIS segment (include these if relevant):
{eligible_benefits if eligible_benefits else 'None — do not mention any conditional bonuses.'}

Styles to include:
- curiosity
- benefit-first
- question
- urgency
- personalization

Return JSON list:
["subject1","subject2","subject3"]
"""

        result = await self._complete_pydantic(
            prompt,
            SubjectLinesSchema,
            temperature=0.7
        )

        return result.model_dump()["subjects"]


    async def _generate_bodies(self, parsed_brief, strategy, history, eligible_benefits, ineligible_benefits):

        segment_name = strategy.get("segment_name", "Unknown")
        segment_desc = strategy.get("description", "")

        prompt = f"""
You are a financial marketing copywriter. Write emails for a SPECIFIC customer segment.

Generate 2 email body variants.

Target Segment: {segment_name}
Segment Description: {segment_desc}

Campaign Brief:
Product: {parsed_brief.get('product')}
Tone: {parsed_brief.get('tone')}
Constraints: {parsed_brief.get('constraints')}
Special Conditions: {parsed_brief.get('special_conditions')}

Global Benefits (apply to ALL segments — ALWAYS include these):
{parsed_brief.get("global_benefits", parsed_brief.get("key_benefits", []))}

ELIGIBLE Conditional Benefits for "{segment_name}" (MUST include these in the email body):
{eligible_benefits if eligible_benefits else 'None — this segment has no conditional bonuses.'}

{history}

Benefit Rules:
- Global benefits: ALWAYS include for every segment.
- Eligible conditional benefits listed above: You MUST EXPLICITLY mention each one with the EXACT numbers. This is mandatory.
- Ineligible benefits listed above: ABSOLUTELY DO NOT mention. Do not hint at them, do not say "if eligible", just completely OMIT.
- DO NOT sum up or combine percentages from different benefit categories.

Goal:
Write a COMPELLING and DETAILED marketing email TAILORED to the "{segment_name}" segment.
The language, tone, and value proposition should resonate specifically with this audience.
Convey ALL relevant benefits from the brief to maximize marketing impact.

Email Rules:
- 100–180 words
- STRICT GROUNDING: You are ONLY allowed to use the interest rates and numbers provided above.
- FORBIDDEN: Do NOT use "1.50%", "2.50%", "0.25%" or any other number UNLESS it is explicitly written in the provided sections above.
- If the brief says "1%", you MUST use "1%". Do NOT change it to any other figure.
- If no specific interest rate is provided, do NOT invent one. Use generic "high-yield" instead ONLY if no numbers exist.
- Highlight the primary benefit in the first two sentences.
- Include CTA once at end.
- Emphasize numbers with **bold**.
- Strictly do NOT hallucinate financial claims.

CTA:
{parsed_brief.get("cta_url")}

Return JSON list:
["body1","body2"]
"""

        result = await self._complete_pydantic(
            prompt,
            EmailBodiesSchema,
            temperature=0.7
        )

        return result.model_dump()["bodies"]


    def _combine_variants(self, subjects, bodies):
        variants = []
        # Reduce search space: 3 subjects x 2 bodies = 6 candidates
        for s in subjects[:3]:
            for b in bodies[:2]:
                variants.append({
                    "subject": s,
                    "body": b
                })
        return variants


    async def _score_variants(self, segment_name, variants):

        prompt = f"""
You are an expert marketing evaluator.

Score email variants from 1–10 based on:

- expected open rate
- clarity of value proposition
- CTA strength
- curiosity or emotional pull
- differentiation

Segment:
{segment_name}

Variants:
{json.dumps(variants, indent=2)}

Return JSON list with:
label
score
"""

        try:
            results = await self._complete_pydantic(
                prompt,
                VariantScoresSchema,
                temperature=0.1
            )

            score_map = {r.label: r.score for r in results.scores}

            for v in variants:
                v["score"] = score_map.get(v.get("label"), 5)

            return variants

        except Exception as e:
            logger.error(f"Variant scoring failed: {e}")

            for v in variants:
                v["score"] = 5

            return variants


    def _validate_segment_benefits(self, segment_name: str, body: str, conditional_benefits: List[str], global_benefits: List[str]) -> str:
        """
        Strips conditional benefits and unauthorized numbers from the email body.
        """
        name_lower = segment_name.lower()
        
        # 1. Identify all ALLOWED numbers/percentages for THIS segment
        eligible_benefits, _ = self._get_eligible_benefits(segment_name, conditional_benefits)
        allowed_text = " ".join(global_benefits + eligible_benefits)
        
        # Extract raw numbers (e.g. 0.85, 9, 1) to be flexible with % vs "percentage point"
        allowed_numbers = set(re.findall(r'(\d+\.?\d*)', allowed_text))
        
        # 2. Identify all POTENTIALLY FORBIDDEN numbers/percentages in the email body
        # We look for numbers followed by % or "percentage" to be specific to financial claims
        body_claims = re.findall(r'(\d+\.?\d*)\s*(?:%|percentage)', body)
        for val in body_claims:
            if val not in allowed_numbers:
                # This number was hallucinated or leaked from another segment
                logger.warning(f"Validator: Stripping unauthorized claim '{val}' from segment '{segment_name}'")
                # Strip the number and any following % or percentage point text
                body = re.sub(rf'{re.escape(val)}\s*(?:%|percentage\s+point[s]?)', "[STRIPPED]", body)

        # 3. Strip the specific benefit phrases for ineligible segments (if LLM included them)
        demographic_map = {
            "senior": ["senior", "citizen", "elderly", "retired", "60+"],
            "female": ["female", "woman", "women", "lady", "ladies"],
            "male": ["male", "man", "men", "gentleman", "gentlemen"],
            "youth": ["youth", "student", "young", "college", "under-25", "teen"],
            "professional": ["professional", "salaried", "corporate", "working"],
            "inactive": ["inactive", "dormant", "re-activate"]
        }

        for benefit in conditional_benefits:
            if benefit in eligible_benefits:
                continue
                
            benefit_lower = benefit.lower()
            required_groups = []
            for group, keywords in demographic_map.items():
                if any(kw in benefit_lower for kw in keywords):
                    required_groups.append(group)

            is_match = True
            for group in required_groups:
                keywords = demographic_map[group]
                if not any(kw in name_lower for kw in keywords):
                    is_match = False
                    break
            
            if not is_match:
                # Segment doesn't match the required demographics for this benefit.
                # If the benefit (or a close match) is present, strip it.
                body = body.replace(benefit, "[STRIPPED]")
                
                # Also strip demographic keywords that shouldn't be here
                for group in required_groups:
                    # Don't strip "male" if the segment is "male young citizens"
                    if group not in name_lower:
                        for kw in demographic_map[group]:
                             body = body.replace(kw, "[STRIPPED]")

        # Cleanup: Replace [STRIPPED] and fix punctuation/spacing
        body = body.replace("[STRIPPED]", "")
        body = " ".join(body.split())
        body = re.sub(r'\s+([.,!?])', r'\1', body)
        body = re.sub(r'([.,!?])\s*\1+', r'\1', body)

        return body


    def _fallback_variants(self, parsed_brief):

        product = parsed_brief.get('product', 'our product')
        body = f"""
Discover **{product}**, designed to offer strong returns and secure growth for your savings.

Learn more about how this investment option can help you grow your wealth.

Explore here:
{parsed_brief.get('cta_url')}
"""

        return [
            {
                "label": "Variant A",
                "subject": f"Discover better returns with {product}",
                "body": body
            },
            {
                "label": "Variant B",
                "subject": "A smarter way to grow your savings",
                "body": body
            }
        ]