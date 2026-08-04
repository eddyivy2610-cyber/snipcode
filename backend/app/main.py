"""
main.py — FastAPI application
==============================
Milestone 4 architecture with Sensor Fusion Engine, AST Validator & Intent Guardrails:

    POST /detect        → raw YOLO detections (debug)
    POST /api/layout    → structured Component tree (debug)
    POST /api/generate  → full HTML + CSS output via Sensor Fusion, Intent Guardrail & AST Validator
"""

from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image
import shutil
import os
import re

from app.services.detector  import detect
from app.services.fusion    import fuse_sensors
from app.services.cleaner   import clean_detections
from app.services.layout    import build_layout
from app.services.validator import validate_ir
from app.services.generator import generate
from app.services.llm       import refine_code_with_llm

app = FastAPI(
    title="Snipcode API",
    description="Screenshot → Sensor Fusion UI tree → AST Validator → HTML/CSS generator",
    version="5.0.0",
)

allowed_origins_raw = os.getenv("ALLOWED_ORIGINS", "*")
allowed_origins = [o.strip() for o in allowed_origins_raw.split(",") if o.strip()]

# Starlette CORSMiddleware requires allow_origins=["*"] alone for allow_all_origins=True
if "*" in allowed_origins or not allowed_origins:
    cors_origins = ["*"]
else:
    cors_origins = allowed_origins

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_origin_regex=r"https://.*\.vercel\.app|http://localhost:\d+|http://127\.0\.0\.1:\d+",
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# ---------------------------------------------------------------------------
# Intent Classifier Guardrail Engine
# ---------------------------------------------------------------------------

def classify_text_intent(prompt_text: str) -> str:
    """
    Classifies prompt text into:
      - 'GREETING'       : e.g. "hello", "hi", "who are you"
      - 'VAGUE_TEXT'     : e.g. "asdf", "test", "foo", "123"
      - 'UI_DESCRIPTION' : e.g. "build a fitness tracker", "login form"
    """
    text = prompt_text.lower().strip()
    if not text:
        return "VAGUE_TEXT"

    # Greetings check
    greetings = {"hello", "hi", "hey", "greetings", "who are you", "what is this", "how are you", "help"}
    if text in greetings:
        return "GREETING"

    # Vague text check (nonsense, very short random words)
    vague = {"asdf", "test", "foo", "bar", "abc", "xyz", "qwer", "123"}
    if text in vague or (len(text) < 4 and not any(w in text for w in ["app", "ui", "nav", "bar"])):
        return "VAGUE_TEXT"

    # UI Keywords check
    ui_keywords = [
        "build", "create", "make", "design", "page", "app", "dashboard", "form",
        "login", "signup", "tracker", "finder", "card", "nav", "header", "button",
        "input", "table", "ui", "screen", "layout"
    ]
    if any(k in text for k in ui_keywords) or len(text) > 8:
        return "UI_DESCRIPTION"

    return "VAGUE_TEXT"


def _generate_greeting_component() -> str:
    return """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <style>
    body { margin: 0; padding: 40px 20px; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #090611; color: #f3f4f6; display: flex; justify-content: center; align-items: center; min-height: 90vh; }
    .card { background: rgba(26, 26, 26, 0.9); border: 1px solid rgba(255,255,255,0.12); border-radius: 24px; padding: 40px; max-width: 520px; text-align: center; box-shadow: 0 25px 50px rgba(0,0,0,0.6); }
    .badge { display: inline-block; padding: 6px 16px; border-radius: 20px; background: rgba(168, 85, 247, 0.2); color: #c084fc; font-size: 12px; font-weight: 600; margin-bottom: 16px; border: 1px solid rgba(168, 85, 247, 0.4); }
    h2 { margin: 0 0 12px 0; font-size: 26px; color: #fff; }
    p { color: #9ca3af; font-size: 14px; line-height: 1.6; margin-bottom: 24px; }
    .features { background: rgba(0,0,0,0.3); padding: 18px; border-radius: 16px; text-align: left; font-size: 13px; color: #d1d5db; border: 1px solid rgba(255,255,255,0.05); }
    .features ul { padding-left: 20px; margin: 8px 0 0 0; }
    .features li { margin-bottom: 8px; }
  </style>
</head>
<body>
  <div class="card">
    <div class="badge">✨ Snipcode Agent Engine</div>
    <h2>Hello! I am your AI UI Compiler</h2>
    <p>Upload any sketch screenshot or describe a web application interface to compile live HTML/CSS components instantly!</p>
    <div class="features">
      <strong>Example Prompts:</strong>
      <ul>
        <li>"Build a dark mode fitness tracking dashboard"</li>
        <li>"Create a login form with email, password & Google OAuth"</li>
        <li>"Design a recipe finder with search filters"</li>
      </ul>
    </div>
  </div>
</body>
</html>"""


def _generate_vague_component(prompt_text: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <style>
    body {{ margin: 0; padding: 40px 20px; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #090611; color: #f3f4f6; display: flex; justify-content: center; align-items: center; min-height: 90vh; }}
    .card {{ background: rgba(26, 26, 26, 0.9); border: 1px solid rgba(255,255,255,0.12); border-radius: 24px; padding: 40px; max-width: 520px; text-align: center; box-shadow: 0 25px 50px rgba(0,0,0,0.6); }}
    .badge {{ display: inline-block; padding: 6px 16px; border-radius: 20px; background: rgba(234, 179, 8, 0.2); color: #fde047; font-size: 12px; font-weight: 600; margin-bottom: 16px; border: 1px solid rgba(234, 179, 8, 0.4); }}
    h2 {{ margin: 0 0 12px 0; font-size: 24px; color: #fff; }}
    p {{ color: #9ca3af; font-size: 14px; line-height: 1.6; margin-bottom: 24px; }}
    .code-chip {{ display: inline-block; background: rgba(255,255,255,0.1); padding: 4px 10px; border-radius: 6px; font-mono; font-size: 13px; color: #f472b6; }}
  </style>
</head>
<body>
  <div class="card">
    <div class="badge">💡 Guidance Prompt</div>
    <h2>Need a Specific UI Description</h2>
    <p>Received input: <span class="code-chip">"{prompt_text}"</span>. Please describe a specific UI component (e.g. <i>"Dashboard", "Login Card"</i>) or attach a screenshot image above!</p>
  </div>
</body>
</html>"""


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _save(file: UploadFile) -> str:
    path = os.path.join(UPLOAD_FOLDER, file.filename)
    with open(path, "wb") as buf:
        shutil.copyfileobj(file.file, buf)
    return path


def _image_size(path: str) -> tuple[int, int]:
    try:
        with Image.open(path) as img:
            return img.size          # (width, height)
    except Exception:
        return 800, 600


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@app.get("/")
@app.get("/health")
def health_check():
    return {
        "status":  "healthy",
        "service": "Snipcode AI Studio API",
        "version": "5.0.0",
        "intent_classifier": "active",
        "fusion_engine": "active",
        "ast_validator": "active"
    }


@app.post("/detect", summary="Raw YOLO detections")
async def detect_endpoint(file: UploadFile = File(...)):
    path = _save(file)
    detections = detect(path)
    return {"filename": file.filename, "detections": detections}


@app.post("/api/layout", summary="Full Sensor Fusion Layout Tree")
async def layout_endpoint(file: UploadFile = File(...)):
    path = _save(file)
    fused_comps = fuse_sensors(path)
    w, h = _image_size(path)
    comps = clean_detections(fused_comps, img_width=w, img_height=h)
    tree = build_layout(comps)
    validated_tree, report = validate_ir(tree)

    return {
        "filename":   file.filename,
        "components": comps,
        "tree":       validated_tree,
        "validation_report": report,
    }


@app.post("/api/generate", summary="Full Sensor Fusion Pipeline with Intent Guardrails & LLM Refinement")
async def generate_endpoint(
    file: UploadFile = File(...),
    prompt: str = Form("")
):
    """
    Full pipeline with Intent Classifier Guardrail & Sensor Fusion:
        1. Perception Check: If screenshot uploaded ➔ Multi-Sensor Fusion
        2. Text Prompt Intent Classification:
           - GREETING ➔ Welcome Agent Component
           - VAGUE_TEXT ➔ Guidance Starter Component
           - UI_DESCRIPTION ➔ Zero-Shot LLM UI Compiler Engine
    """
    path = _save(file)
    fused_comps = []
    try:
        fused_comps = fuse_sensors(path)
    except Exception as fusion_err:
        print(f"[Generate Endpoint] Perception sensor warning/fallback: {fusion_err}")

    w, h = _image_size(path)

    # Clean detections safely
    comps = clean_detections(fused_comps, img_width=w, img_height=h)

    # INTENT GUARDRAIL: No visual components detected (blank input image or text-only)
    if len(comps) == 0:
        intent = classify_text_intent(prompt)
        
        if intent == "GREETING":
            return {
                "filename": file.filename,
                "components": [],
                "tree": [{"type": "GreetingNode", "id": "greeting_1"}],
                "validation_report": {"valid": True, "errors": [], "warnings": ["Greeting intent handled."]},
                "html": _generate_greeting_component(),
                "css": "body { background: #090611; }",
            }
            
        elif intent == "VAGUE_TEXT" and not file.filename:
            return {
                "filename": file.filename,
                "components": [],
                "tree": [{"type": "VagueNode", "id": "vague_1"}],
                "validation_report": {"valid": True, "errors": [], "warnings": ["Vague input text handled."]},
                "html": _generate_vague_component(prompt),
                "css": "body { background: #090611; }",
            }

    # STANDARD PIPELINE: Image Detections or UI Description Intent
    tree = build_layout(comps)
    validated_tree, report = validate_ir(tree)
    draft_html, draft_css = generate(validated_tree)

    # LLM Refinement via Groq API (Qwen 2.5 Coder 32B / Llama 3.3 70B)
    try:
        final_html, final_css = refine_code_with_llm(
            component_json=comps,
            layout_tree=validated_tree,
            draft_html=draft_html,
            draft_css=draft_css,
            screenshot_path=path
        )
        if not final_html or len(final_html.strip()) < 10:
            final_html = draft_html
    except Exception as llm_err:
        print(f"[Generate Endpoint] LLM refinement fallback to draft code: {llm_err}")
        final_html = draft_html
        final_css = draft_css

    return {
        "filename":   file.filename,
        "components": comps,
        "tree":       validated_tree,
        "validation_report": report,
        "html":       final_html,
        "css":        final_css,
    }