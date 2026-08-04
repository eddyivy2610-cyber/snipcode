"""
services/llm.py
===============
Post-Processing Refinement Module (Phase 6 Enriched Context):
  Refines the rule-generated HTML/CSS draft using Qwen2.5-Coder:
    - Primary: Free Groq Cloud API (Qwen 2.5 Coder 32B) via GROQ_API_KEY
    - Fallback 1: Local Ollama (qwen2.5-coder:7b-instruct)
    - Fallback 2: Rule-Based Compiler Output
"""

from __future__ import annotations

import base64
import logging
import os
import requests
from typing import Dict, Any
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

# Free Cloud & Local LLM configurations
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL = os.getenv("GROQ_MODEL", "qwen-2.5-coder-32b")

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://127.0.0.1:11434/api/generate")
OLLAMA_MODEL = os.getenv("LLM_MODEL_NAME", "qwen2.5-coder:7b-instruct")

SYSTEM_PROMPT = """You are an expert Frontend AI Refinement Engine.
You are improving draft HTML to match modern, responsive, professional UI designs based on semantic IR nodes, component roles, visual variants, and layout structure.

CRITICAL CONSTRAINTS:
1. DO NOT remove any form inputs, buttons, or text labels.
2. DO NOT change OCR text values or button text.
3. PRESERVE form structures and input labels (<label> and <input>).
4. RESPECT component roles (e.g. role="submit" -> type="submit", role="search" -> type="search").
5. RESPECT visual variants (e.g. variant="primary" -> primary button style, variant="outlined" -> outlined border style).
6. Reconstruct centered card panels with rounded corners, subtle shadows, and padding.
7. Use semantic HTML5 tags (<header>, <main>, <form>, <section>, <footer>).
8. Improve visual hierarchy, spacing, padding, margins, and flex/grid alignment using exact bounding box coordinates provided.

Return clean, valid HTML only inside ```html ``` code blocks. Do not include conversational commentary.
"""


def query_groq_qwen(prompt: str) -> str | None:
    """Query Qwen2.5-Coder-32B via Free Groq Cloud API."""
    if not GROQ_API_KEY:
        return None

    try:
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": GROQ_MODEL,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.1,
            "max_tokens": 4096,
        }
        response = requests.post(GROQ_URL, json=payload, headers=headers, timeout=20)
        if response.status_code == 200:
            res_json = response.json()
            content = res_json["choices"][0]["message"]["content"]
            logger.info(f"[LLM] Groq API Qwen2.5-Coder-32B response received successfully.")
            return content
        else:
            logger.warning(f"[LLM] Groq API returned HTTP status {response.status_code}: {response.text}")
    except Exception as e:
        logger.warning(f"[LLM] Groq API request failed: {e}")
    return None


def query_ollama_qwen(prompt: str, images_payload: list[str]) -> str | None:
    """Query Qwen2.5-Coder locally via Ollama."""
    try:
        payload = {
            "model": OLLAMA_MODEL,
            "prompt": prompt,
            "system": SYSTEM_PROMPT,
            "stream": False,
            "options": {"temperature": 0.1, "top_p": 0.9},
        }
        if images_payload:
            payload["images"] = images_payload

        response = requests.post(OLLAMA_URL, json=payload, timeout=60)
        if response.status_code == 200:
            res_json = response.json()
            return res_json.get("response", "").strip()
    except Exception as e:
        logger.info(f"[LLM] Local Ollama unreachable: {e}")
    return None


def refine_code_with_llm(
    component_json: list[dict],
    layout_tree: list[dict],
    draft_html: str,
    draft_css: str,
    screenshot_path: str | None = None
) -> tuple[str, str]:
    """
    Refine draft HTML/CSS using Qwen2.5-Coder as a post-processing refinement module.
    Checks Groq Cloud API first, falls back to local Ollama, then rule-based draft.
    """
    os.makedirs("generated", exist_ok=True)
    try:
        with open("generated/draft.html", "w", encoding="utf-8") as f:
            f.write(draft_html)
    except Exception as e:
        logger.warning(f"Failed to log draft HTML: {e}")

    # Prepare visual context if screenshot exists
    images_payload = []
    if screenshot_path and os.path.exists(screenshot_path):
        try:
            with open(screenshot_path, "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read()).decode("utf-8")
                images_payload.append(encoded_string)
        except Exception as img_err:
            logger.warning(f"Failed to base64 encode screenshot: {img_err}")

    # Format multi-sensor IR
    enriched_ir = []
    for c in component_json:
        bbox = c.get("bbox", [0, 0, 0, 0])
        text_val = c.get("text", "") or (c.get("content", {}).get("text", "") if isinstance(c.get("content"), dict) else "")
        enriched_ir.append({
            "id": c.get("id", f"node_{len(enriched_ir)+1}"),
            "type": c.get("type"),
            "role": c.get("role", "generic"),
            "variant": c.get("variant", "standard"),
            "content": {"text": text_val},
            "bbox_pixels": {
                "xmin": round(bbox[0], 1),
                "ymin": round(bbox[1], 1),
                "xmax": round(bbox[2], 1),
                "ymax": round(bbox[3], 1),
                "width": round(bbox[2] - bbox[0], 1),
                "height": round(bbox[3] - bbox[1], 1),
            },
            "confidence": round(c.get("confidence", 0), 2),
            "source": c.get("source", ["YOLO", "EasyOCR", "ScreenParser"]),
        })

    prompt = f"""
1. Multi-Sensor Semantic IR Nodes (YOLO + EasyOCR + ScreenParser):
{enriched_ir}

2. Semantic Layout Tree Hierarchy (JSON):
{layout_tree}

3. Rule-Based Draft HTML:
```html
{draft_html}
```

Refine this HTML layout following strict rules. Correct spacing, visual alignment, container padding, responsive flex/grid structure, and component semantics matching the multi-sensor IR provided.
"""

    refined_html = draft_html

    # Step 1: Try Free Groq Cloud Qwen2.5-Coder-32B
    response_text = query_groq_qwen(prompt)

    # Step 2: Fallback to Local Ollama Qwen2.5-Coder
    if not response_text:
        response_text = query_ollama_qwen(prompt, images_payload)

    # Step 3: Parse output HTML
    if response_text:
        if "```html" in response_text:
            refined_html = response_text.split("```html")[1].split("```")[0].strip()
        elif "```" in response_text:
            parts = response_text.split("```")
            if len(parts) >= 3:
                refined_html = parts[1].strip()
            else:
                refined_html = response_text.replace("```", "").strip()
        else:
            refined_html = response_text

        try:
            with open("generated/refined.html", "w", encoding="utf-8") as f:
                f.write(refined_html)
        except Exception as e:
            logger.warning(f"Failed to log refined HTML: {e}")

    return refined_html, draft_css
