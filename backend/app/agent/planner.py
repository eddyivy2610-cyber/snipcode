"""
agent/planner.py
================
Step Reasoning & Action Planner.

Decides the next action in the 4-stage agent loop based on AST state & similarity scores:
  - UNDERSTAND  ➔ Build initial IR v5.0 AST
  - REPAIR      ➔ Auto-correct AST lint errors or missing labels
  - GENERATE    ➔ Compile AST into target framework code (React/HTML)
  - VERIFY      ➔ Headless visual similarity check against original
  - FINISH      ➔ Accept compilation output
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


class Planner:
    """
    Action Decision Engine for UI Compiler Agent.
    """

    def decide_next_step(
        self,
        current_stage: str,
        ast: List[Dict[str, Any]],
        validation_report: Dict[str, Any],
        similarity_score: float,
        retry_count: int,
        max_retries: int = 3
    ) -> str:
        """
        Determine the next operational stage.
        """
        if current_stage == "INIT":
            return "UNDERSTAND"

        if current_stage == "UNDERSTAND":
            return "REPAIR"

        if current_stage == "REPAIR":
            # If validation failed or retry needed
            if validation_report.get("errors") and retry_count < max_retries:
                logger.info("[Planner] AST errors found -> Re-running REPAIR stage.")
                return "REPAIR"
            return "GENERATE"

        if current_stage == "GENERATE":
            return "VERIFY"

        if current_stage == "VERIFY":
            if similarity_score >= 0.85:
                logger.info(f"[Planner] Similarity score ({similarity_score:.2f}) >= 0.85 -> Stage FINISH.")
                return "FINISH"
            elif retry_count < max_retries:
                logger.info(f"[Planner] Similarity score ({similarity_score:.2f}) below threshold -> Retrying REPAIR.")
                return "REPAIR"
            else:
                logger.info(f"[Planner] Reached max retries ({max_retries}) -> Forcing FINISH.")
                return "FINISH"

        return "FINISH"
