"""
pipeline/ingestion.py
─────────────────────
Ingests a PDF using PyMuPDF (fitz), extracts raw text, then segments it
into logical clauses/sections using:
  1. Regex heuristics (numbered sections, ALL-CAPS headings)
  2. An LLM fallback for ambiguous boundaries
"""

import re
try:
    import fitz  # PyMuPDF < 1.24
except ImportError:
    import pymupdf as fitz  # PyMuPDF >= 1.24
from typing import List, Dict

import os

SECTION_PATTERNS = [
    r"^(\d+\.\s+[A-Z][A-Za-z\s]{3,60})$",         # 1. Definitions
    r"^([A-Z][A-Z\s]{4,60})$",                      # ALL CAPS HEADING
    r"^(Section\s+\d+[\.:]\s+.{3,60})$",            # Section 1: ...
    r"^(Article\s+[IVXLC\d]+[\.:]\s+.{3,60})$",     # Article IV: ...
    r"^(\([a-z]\)\s+.{3,60})$",                     # (a) sub-clause
]

COMPILED = [re.compile(p, re.MULTILINE) for p in SECTION_PATTERNS]


def extract_text_from_pdf(path: str) -> str:
    """Extract raw text from all pages of a PDF."""
    doc = fitz.open(path)
    pages = []
    for page in doc:
        text = page.get_text("text")
        pages.append(text)
    doc.close()
    return "\n".join(pages)


def is_heading(line: str) -> bool:
    line = line.strip()
    if not line:
        return False
    for pattern in COMPILED:
        if pattern.match(line):
            return True
    return False


def regex_segment(text: str) -> List[Dict]:
    """Split text into segments based on detected headings."""
    lines = text.split("\n")
    segments = []
    current_title = "Preamble"
    current_lines = []

    for line in lines:
        if is_heading(line):
            if current_lines:
                body = " ".join(l.strip() for l in current_lines if l.strip())
                if body:
                    segments.append({"title": current_title, "text": body})
            current_title = line.strip()
            current_lines = []
        else:
            current_lines.append(line)

    # flush last segment
    if current_lines:
        body = " ".join(l.strip() for l in current_lines if l.strip())
        if body:
            segments.append({"title": current_title, "text": body})

    return segments


def llm_segment(text: str) -> List[Dict]:
    """
    Fallback: use Groq LLM to split document into sections.
    """

    from groq import Groq
    import json

    client = Groq(api_key=os.getenv("GROQ_API_KEY"))

    prompt = f"""
Split the following legal document into sections.

Return ONLY valid JSON in this exact format:
[
  {{
    "title": "Section title",
    "text": "Section content"
  }}
]

Rules:
- No markdown (*, |, #, -)
- No explanations
- No extra text
- Only return JSON array

Document:
{text[:6000]}
"""

    try:
        response = client.chat.completions.create(
            model="llama3-70b-8192",  # or mixtral
            messages=[{"role": "user", "content": prompt}],
        )

        raw = response.choices[0].message.content.strip()

        # 🔥 CLEAN JSON (important for Groq)
        start = raw.find("[")
        end = raw.rfind("]") + 1
        cleaned = raw[start:end]

        data = json.loads(cleaned)

        return data if isinstance(data, list) else []

    except Exception as e:
        print(f"[ingestion] Groq segmentation failed: {e}")
        return []


def ingest_pdf(path: str) -> List[Dict]:
    """
    Main entry point.
    Returns list of segment dicts: {title, text}
    """
    raw_text = extract_text_from_pdf(path)

    if not raw_text.strip():
        raise ValueError("PDF appears to be a scanned image with no extractable text. "
                         "Please provide a text-based PDF.")

    segments = regex_segment(raw_text)

    # If regex fails to find meaningful structure, fall back to LLM
    if len(segments) < 3:
        print("[ingestion] Regex found < 3 segments, falling back to LLM segmentation.")
        try:
            if len(segments) < 3:
                print()
        except Exception as e:
            print("[ingestion] Using fallback single segment (no LLM).")
            segments = [{"title": "Full Document", "text": raw_text}]

    print(f"[ingestion] Extracted {len(segments)} segments from '{path}'")
    return segments
