"""
OptimizationEngine — Deterministic Multi-Armed Bandit optimizer.

Improvements over previous version:
- Removes LLM reasoning
- Uses epsilon-greedy bandit algorithm
- Computes weighted performance scores
- Supports exploration vs exploitation
- Maintains stability across loops
"""

import logging
import random
from typing import Dict, Any, List, DefaultDict, Optional
from collections import defaultdict

logger = logging.getLogger(__name__)


class OptimizationEngine:

    def __init__(self, epsilon: float = 0.3):
        """
        epsilon = exploration probability
        0.3 means ~30% exploration, ~70% exploitation
        """
        self.epsilon = epsilon

    async def run(
        self,
        curr_metrics: List[Dict[str, Any]],
        segments_info: Optional[List[Dict[str, Any]]] = None,
        optimization_goal: str = "click_rate",
    ) -> Dict[str, Any]:
        """
        Analyze metrics and decide optimization actions.

        Args:
            curr_metrics: Performance metrics from the latest campaign run
            segments_info: Segment metadata including customer counts
            optimization_goal: What to optimize for — "click_rate" or "open_rate"

        Returns:
        {
            "decisions": [...],
            "stop_optimization": bool
        }
        """

        if not curr_metrics:
            logger.warning("OptimizationEngine: No metrics received. Continuing loop to maintain orchestration.")
            return {"decisions": [], "stop_optimization": False}

        # Determine scoring weights based on optimization goal from the brief
        if optimization_goal == "open_rate":
            click_weight, open_weight = 0.2, 0.8
        elif optimization_goal == "click_rate":
            click_weight, open_weight = 0.8, 0.2
        else:
            # Default balanced weighting favoring clicks
            click_weight, open_weight = 0.7, 0.3

        logger.info(
            f"OptimizationEngine: Using optimization_goal='{optimization_goal}' → "
            f"click_weight={click_weight}, open_weight={open_weight}"
        )

        # Build segment size lookup from segments_info or metrics
        segment_sizes: Dict[str, int] = {}
        all_segment_names: set = set()
        if segments_info:
            for s in segments_info:
                name = s.get("name", "")
                segment_sizes[name] = s.get("customer_count", 1)
                all_segment_names.add(name)

        # Group metrics by segment
        segment_metrics: DefaultDict[str, List[Dict[str, Any]]] = defaultdict(list)

        for m in curr_metrics:
            segment_name = m.get("segment_name", "Unknown")
            segment_metrics[segment_name].append(m)
            all_segment_names.add(segment_name)

        decisions = []
        stop_optimization = False

        for segment_name, variants in segment_metrics.items():

            # Compute impact-weighted scores
            seg_size = segment_sizes.get(segment_name, 1)

            for v in variants:
                open_rate = v.get("open_rate", 0)
                click_rate = v.get("click_rate", 0)

                raw_score = (click_weight * click_rate) + (open_weight * open_rate)
                impact = seg_size * raw_score

                v["score"] = impact
                v["raw_score"] = raw_score

            logger.info(
                f"OptimizationEngine reasoning: Segment '{segment_name}' "
                f"(size={seg_size}) — impact-weighted scores applied."
            )

            # Determine best variant
            best_variant = max(variants, key=lambda x: x["score"])
            best_variant_label = best_variant.get("variant_label")  # fixed: was "variant"

            # Decide explore vs exploit
            force_explore = best_variant.get("raw_score", 0) == 0.0

            if force_explore:
                logger.info(
                    f"OptimizationEngine reasoning: Forcing exploration for segment '{segment_name}' "
                    f"because current best raw_score is 0.0 (0% CTR/Open Rate)"
                )

            if not force_explore and random.random() > self.epsilon:

                # Exploit
                decision = {
                    "segment_name": segment_name,
                    "action": "exploit",
                    "best_variant": best_variant_label
                }

                logger.info(
                    f"Exploiting best variant {best_variant_label} "
                    f"for segment {segment_name}"
                )

            else:

                # Explore
                decision = {
                    "segment_name": segment_name,
                    "action": "explore",
                    "best_variant": best_variant_label,
                    "exploration_strategy": {
                        "subject_mutation": True,
                        "emoji_test": True,
                        "send_time_adjustment": True
                    }
                }

                logger.info(
                    f"Exploring new variants for segment {segment_name}"
                )

            decision["impact"] = best_variant.get("score", 0)
            decisions.append(decision)

        # Ensure ALL segments have optimization decisions — segments with no metrics get forced exploration
        covered_segments = {d["segment_name"] for d in decisions}
        for seg_name in all_segment_names:
            if seg_name not in covered_segments:
                logger.info(
                    f"OptimizationEngine: Segment '{seg_name}' had no metrics — forcing exploration"
                )
                decisions.append({
                    "segment_name": seg_name,
                    "action": "explore",
                    "best_variant": None,
                    "exploration_strategy": {
                        "subject_mutation": True,
                        "emoji_test": True,
                        "send_time_adjustment": True
                    },
                    "impact": 0,
                })

        # Sort by impact so large high-performing segments are prioritized
        decisions.sort(key=lambda d: d.get("impact", 0), reverse=True)

        logger.info(
            f"OptimizationEngine reasoning: Prioritized segments by impact — "
            f"{[d['segment_name'] for d in decisions]}"
        )

        return {
            "decisions": decisions,
            "stop_optimization": stop_optimization
        }