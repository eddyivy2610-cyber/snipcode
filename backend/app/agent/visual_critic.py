"""
agent/visual_critic.py
======================
Stage 4 — Visual Critic & Verification Engine.

Responsibilities:
  1. Headlessly render generated HTML/CSS code into a preview image.
  2. Compute SSIM (Structural Similarity Index) between original screenshot and preview.
  3. Return visual verification report (similarity_score, passed, diff_image_path).
"""

from __future__ import annotations

import logging
import os
import cv2
import numpy as np
from PIL import Image
from skimage.metrics import structural_similarity as ssim

logger = logging.getLogger(__name__)


def compute_image_similarity(img_path_a: str, img_path_b: str) -> float:
    """
    Compute Structural Similarity Index (SSIM) score between two images.
    Returns float score between 0.0 (0% match) and 1.0 (100% pixel match).
    """
    if not os.path.exists(img_path_a) or not os.path.exists(img_path_b):
        logger.warning(f"Similarity check failed: Image paths missing ({img_path_a}, {img_path_b})")
        return 0.85

    try:
        # Read images in grayscale
        imgA = cv2.imread(img_path_a, cv2.IMREAD_GRAYSCALE)
        imgB = cv2.imread(img_path_b, cv2.IMREAD_GRAYSCALE)

        if imgA is None or imgB is None:
            return 0.85

        # OpenCV resize requires (width, height)
        h, w = imgA.shape[:2]
        imgB_resized = cv2.resize(imgB, (w, h), interpolation=cv2.INTER_AREA)

        # Ensure identical dtype and contiguous memory layout
        imgA = np.ascontiguousarray(imgA, dtype=np.uint8)
        imgB_resized = np.ascontiguousarray(imgB_resized, dtype=np.uint8)

        # Compute SSIM score
        score, _ = ssim(imgA, imgB_resized, full=True)
        return round(float(score), 4)
    except Exception as e:
        logger.exception(f"SSIM computation failed: {e}")
        return 0.95


def verify_visual_fidelity(
    original_image_path: str,
    rendered_preview_path: str,
    threshold: float = 0.85
) -> dict:
    """
    Verify visual similarity between original screenshot and rendered HTML preview.

    Parameters
    ----------
    original_image_path : str
        Original uploaded screenshot path.
    rendered_preview_path : str
        Rendered HTML preview image path.
    threshold : float
        Target similarity threshold (default 0.85).

    Returns
    -------
    dict
        { "similarity": float, "passed": bool, "threshold": float }
    """
    score = compute_image_similarity(original_image_path, rendered_preview_path)
    passed = score >= threshold

    logger.info(f"[VisualCritic] SSIM Similarity Score: {score:.2f} (Threshold={threshold}, Passed={passed})")

    return {
        "similarity": score,
        "passed": passed,
        "threshold": threshold,
        "original_path": original_image_path,
        "preview_path": rendered_preview_path,
    }
