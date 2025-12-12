import os
import json
import re
import google.generativeai as genai
from PIL import Image
import os
from dotenv import load_dotenv

# This loads the variables from .env immediately
load_dotenv()

# Now you can use them anywhere
API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise ValueError("No API Key found! Check your .env or GitHub Secrets.")


if API_KEY:
    genai.configure(api_key=API_KEY)

# 'gemini-1.5-flash' is fast, cheap/free, and multimodal (reads text & images)
MODEL_NAME = "gemini-2.5-flash"

# Strict Schema to force the AI to return consistent JSON
RESPONSE_SCHEMA = {
    "type": "object",
    "properties": {
        "metadata": {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "email": {"type": "string"},
                "phone": {"type": "string"},
                "links": {"type": "array", "items": {"type": "string"}},
                "detected_skills": {"type": "array", "items": {"type": "string"}},
            }
        },
        "content": {
            "type": "object",
            "properties": {
                "summary": {"type": "string"},
                "work_experience": {"type": "array", "items": {"type": "string"}},
                "education": {"type": "array", "items": {"type": "string"}},
                "projects": {"type": "array", "items": {"type": "string"}},
                "certifications": {"type": "array", "items": {"type": "string"}}
            }
        }
    }
}

def extract_entities(text_content, file_path=None, blind_mode=False):
    """
    Main extraction function using Generative AI.
    
    Args:
        text_content (str): Raw text from PDF/DOCX.
        file_path (str): Path to image file (if processing an image).
        blind_mode (bool): If True, redacts PII.
    """
    # Default structure in case of failure
    data = {
        "metadata": {
            "name": "Unknown", "email": None, "phone": None, 
            "links": [], "detected_skills": [],
            "warnings": []
        },
        "content": {
            "professional summary": "", "experience": [], 
            "education": [], "projects": [], "certifications": []
        }
    }

    if not API_KEY:
        data["metadata"]["warnings"].append("Missing GEMINI_API_KEY. AI extraction skipped.")
        return data

    try:
        model = genai.GenerativeModel(MODEL_NAME)
        
        # --- MODE SELECTION: VISION VS TEXT ---
        if file_path:
            print(f"👀 AI Vision Mode: Processing {file_path}")
            img = Image.open(file_path)
            
            # IMPROVED PROMPT
            prompt = """
            Analyze this resume image. Extract data into strict JSON.
            CRITICAL INSTRUCTION: The Candidate Name is almost always the largest text at the very top. Find it first.
            
            Rules:
            1. Extract Name, Email, Phone (Look at the header/margins).
            2. Summarize work experience items.
            3. Extract technical skills.
            """
            content_payload = [prompt, img]
        else:
            # TEXT MODE: Pass the raw text string
            clean_text = text_content[:20000] # Safe limit for high speed
            prompt = f"""
            You are an expert HR Resume Parser. Extract data from the text below into strict JSON.
            
            RESUME TEXT:
            {clean_text}
            """
            content_payload = prompt

        # --- EXECUTE AI CALL ---
        response = model.generate_content(
            content_payload,
            generation_config=genai.GenerationConfig(
                response_mime_type="application/json",
                response_schema=RESPONSE_SCHEMA
            )
        )

        # --- PARSE RESPONSE ---
        parsed = json.loads(response.text)
        
        # Map AI Schema -> Your App's Legacy Structure
        meta = parsed.get("metadata", {})
        content = parsed.get("content", {})
        
        data["metadata"]["name"] = meta.get("name")
        data["metadata"]["email"] = meta.get("email")
        data["metadata"]["phone"] = meta.get("phone")
        data["metadata"]["links"] = meta.get("links", [])
        data["metadata"]["detected_skills"] = meta.get("detected_skills", [])
        
        # Flatten lists for CSV export compatibility
        data["content"]["professional summary"] = content.get("summary", "")
        data["content"]["experience"] = content.get("work_experience", [])
        data["content"]["education"] = content.get("education", [])
        data["content"]["projects"] = content.get("projects", [])
        data["content"]["certifications"] = content.get("certifications", [])

    except Exception as e:
        error_msg = f"AI Extraction Error: {str(e)}"
        print(f"❌ {error_msg}")
        data["metadata"]["warnings"].append(error_msg)

    # --- BLIND MODE REDACTION ---
    if blind_mode:
        for field in ["name", "email", "phone"]:
            data["metadata"][field] = "[REDACTED]"
        data["metadata"]["links"] = ["[REDACTED]"]

    return data

def calculate_match_score(resume_text, jd_text):
    """
    Robust Jaccard Similarity (Token-based)
    """
    if not jd_text or not resume_text: return 0
    
    def tokenize(text):
        # Split by non-alphanumeric, lowercase
        return set(re.findall(r'\w+', text.lower()))
    
    resume_tokens = tokenize(resume_text)
    jd_tokens = tokenize(jd_text)
    
    if not jd_tokens: return 0
    
    # Calculate intersection
    intersection = resume_tokens.intersection(jd_tokens)
    
    # Standard Jaccard Index
    score = len(intersection) / len(jd_tokens) * 100
    
    # Boost factor: A 25% match is actually quite good in keyword matching
    final_score = min(100, int(score * 3.0))
    
    return final_score