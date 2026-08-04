"""
agent/tools.py
==============
Tool Wrappers for UI Compiler Agent.

Wraps low-level services as callable agent tools:
  - understand(image_path) ➔ Runs Sensor Fusion (YOLO + EasyOCR + ScreenParser) ➔ Returns IR v5.0 AST
  - repair(ast) ➔ Runs AST Validator Linter ➔ Returns Auto-Corrected AST & Problem List
  - generate(ast, target="html") ➔ Runs Compiler Target Generator ➔ Returns Code Output
  - verify(original_img, preview_img) ➔ Runs Visual Critic SSIM ➔ Returns Verification Report
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List

from app.services.fusion import fuse_sensors
from app.services.validator import validate_ir
from app.services.generator import generate as run_generator
from app.agent.visual_critic import verify_visual_fidelity

logger = logging.getLogger(__name__)


def tool_understand(image_path: str) -> List[Dict[str, Any]]:
    """Stage 1: Observation & Perception Tool (YOLO + EasyOCR + ScreenParser)."""
    logger.info(f"[Tool: Understand] Processing image: {image_path}")
    return fuse_sensors(image_path)


def tool_repair(ast: List[Dict[str, Any]]) -> tuple[List[Dict[str, Any]], Dict[str, Any]]:
    """Stage 2: Repair & Validation Tool (AST Linter & Auto-Corrector)."""
    logger.info(f"[Tool: Repair] Validating & repairing AST ({len(ast)} root nodes)...")
    return validate_ir(ast)


def tool_generate(ast: List[Dict[str, Any]], target: str = "html") -> tuple[str, str]:
    """Stage 3: Multi-Target Code Generator Tool (HTML, React, Next.js)."""
    logger.info(f"[Tool: Generate] Emitting target code for framework: '{target}'")
    return run_generator(ast)


def tool_verify(original_image_path: str, preview_image_path: str, threshold: float = 0.85) -> Dict[str, Any]:
    """Stage 4: Visual Verification Tool (Headless SSIM Comparator)."""
    logger.info(f"[Tool: Verify] Verifying similarity against original screenshot...")
    return verify_visual_fidelity(original_image_path, preview_image_path, threshold)
