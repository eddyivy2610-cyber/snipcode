"""
services/cleaner.py
===================
Detection Cleanup Engine:
  1. Non-Maximum Suppression (NMS) via IoU thresholding to eliminate duplicate/overlapping boxes.
  2. Containment Deduplication to remove redundant inner boxes with duplicate text.
  3. Micro-box & noise filtering.
"""

import re
from typing import List, Dict, Any


def compute_iou(boxA: List[float], boxB: List[float]) -> float:
    """Calculate Intersection over Union (IoU) between two [xmin, ymin, xmax, ymax] boxes."""
    axmin, aymin, axmax, aymax = boxA
    bxmin, bymin, bxmax, bymax = boxB

    ixmin = max(axmin, bxmin)
    iymin = max(aymin, bymin)
    ixmax = min(axmax, bxmax)
    iymax = min(aymax, bymax)

    if ixmax <= ixmin or iymax <= iymin:
        return 0.0

    intersection = (ixmax - ixmin) * (iymax - iymin)
    areaA = (axmax - axmin) * (aymax - aymin)
    areaB = (bxmax - bxmin) * (bymax - bymin)

    union = areaA + areaB - intersection
    return intersection / union if union > 0 else 0.0


def is_contained(inner_box: List[float], outer_box: List[float], threshold: float = 0.85) -> bool:
    """Check if inner_box is almost completely contained within outer_box."""
    ixmin, iymin, ixmax, iymax = inner_box
    oxmin, oymin, oxmax, oymax = outer_box

    c_xmin = max(ixmin, oxmin)
    c_ymin = max(iymin, oymin)
    c_xmax = min(ixmax, oxmax)
    c_ymax = min(iymax, oymax)

    if c_xmax <= c_xmin or c_ymax <= c_ymin:
        return False

    intersection = (c_xmax - c_xmin) * (c_ymax - c_ymin)
    inner_area = (ixmax - ixmin) * (iymax - iymin)

    return (intersection / inner_area) >= threshold if inner_area > 0 else False


def is_desktop_chrome_noise(comp: Dict[str, Any], img_width: float, img_height: float) -> bool:
    """Detect if a component is browser Chrome UI, address bar URL, window controls, or Windows taskbar tray indicator."""
    bbox = comp["bbox"]
    text = comp.get("text", "").strip()
    text_lower = text.lower()
    
    width = bbox[2] - bbox[0]
    height = bbox[3] - bbox[1]
    y_center = (bbox[1] + bbox[3]) / 2
    
    # 0. Filter out massive outer full-viewport bounding boxes
    if img_width > 0 and img_height > 0:
        if (width / img_width) >= 0.96 and (height / img_height) >= 0.96:
            return True

    # 1. Top Browser Header Region (top 18% or top 120px)
    limit_y_top = max(120.0, img_height * 0.18) if img_height > 0 else 120.0
    if y_center < limit_y_top or bbox[1] < limit_y_top:
        # Browser chrome keywords, local file paths, address bar URLs
        noise_keywords = (
            "c:users", "localhost", "127.0.0.1", ".html", ".htm", "http:", "https:",
            "relaunch", "update", "chrome", "file", "edit", "view", "history",
            "bookmarks", "profiles", "tab", "tabs", "extensions", "reload", "address bar",
            "search google", "type a url"
        )
        if any(kw in text_lower for kw in noise_keywords):
            return True
        # Exact match for system menu items in header
        if text_lower in ("file", "edit", "view", "history", "bookmarks", "profiles", "tab", "window", "help"):
            return True

    # 2. Bottom Taskbar Region (bottom 12% or bottom 70px)
    limit_y_bottom = (img_height - 70.0) if img_height > 0 else 0.0
    is_bottom = (img_height > 0 and y_center > img_height * 0.88) or (limit_y_bottom > 0 and y_center > limit_y_bottom)
    if is_bottom:
        # Tray icons, language indicators, dates, times
        tray_keywords = ("eng", "intl", "clock", "wifi", "battery", "volume", "speakers", "notification")
        if text_lower in tray_keywords:
            return True
        if re.search(r'\d{1,2}[/\-.]\d{1,2}[/\-.]\d{2,4}', text):
            return True
        if re.search(r'\b\d{1,2}[:.]\d{2}\s*(?:am|pm)?\b', text_lower):
            return True

    return False


def clean_detections(
    components: List[Dict[str, Any]],
    iou_threshold: float = 0.55,
    min_width: float = 8.0,
    min_height: float = 8.0,
    img_width: float = 0.0,
    img_height: float = 0.0
) -> List[Dict[str, Any]]:
    """
    Clean flat component list by removing:
      - Browser chrome UI or Windows taskbar noise
      - Micro boxes smaller than min_width / min_height
      - Highly overlapping duplicates (NMS)
      - Contained duplicates with identical text
    """
    # 1. Filter out micro boxes and desktop chrome noise
    filtered = []
    for c in components:
        bbox = c.get("bbox") or c.get("box") or [0, 0, 0, 0]
        c["bbox"] = bbox
        width = bbox[2] - bbox[0]
        height = bbox[3] - bbox[1]

        if width < min_width or height < min_height:
            continue

        if is_desktop_chrome_noise(c, img_width, img_height):
            continue

        # Filter empty low-confidence links/texts and single-digit OCR noise
        c_text = c.get("text", "").strip()
        c_type = c.get("type", "").lower()
        c_conf = c.get("confidence", 0.0)
        
        if not c_text and c_conf < 0.60 and c_type in ("link", "text", "button"):
            continue
        if len(c_text) == 1 and c_text in "0123456789" and c_conf < 0.45:
            continue

        filtered.append(c)

    # 2. Sort by confidence descending so higher-confidence components are prioritized
    filtered.sort(key=lambda x: x.get("confidence", 0.0), reverse=True)

    cleaned = []
    for comp in filtered:
        box_a = comp["bbox"]
        text_a = comp.get("text", "").strip()
        keep = True

        for existing in cleaned:
            box_b = existing["bbox"]
            text_b = existing.get("text", "").strip()
            iou = compute_iou(box_a, box_b)

            # Rule A: High IoU overlap (duplicate detection) -> drop lower confidence
            if iou >= iou_threshold:
                keep = False
                if not text_b and text_a:
                    existing["text"] = text_a
                    existing["text_confidence"] = comp.get("text_confidence", 0.0)
                break

            # Rule B: Containment & Substring Text Deduplication
            if is_contained(box_a, box_b, threshold=0.70) or is_contained(box_b, box_a, threshold=0.70):
                if not text_a or text_a.lower() in text_b.lower() or text_b.lower() in text_a.lower():
                    keep = False
                    # Transfer OCR text if existing had none
                    if not text_b and text_a:
                        existing["text"] = text_a
                        existing["text_confidence"] = comp.get("text_confidence", 0.0)
                    break

        if keep:
            cleaned.append(comp)

    return cleaned
