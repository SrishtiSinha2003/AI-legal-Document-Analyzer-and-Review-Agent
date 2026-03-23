"""
pipeline/ner.py
───────────────
Legal Named Entity Recognition using spaCy (en_core_web_trf).
Extracts: PARTY, DATE, MONEY, JURISDICTION, DURATION, PENALTY.

Fine-tuning note: for production, fine-tune on CUAD dataset labels.
This file provides a working baseline with pattern-based rulers + transformer model.
"""

import spacy
from spacy.pipeline import EntityRuler
from typing import List, Dict

# ---------------------------------------------------------------------------
# Load model once at module level
# ---------------------------------------------------------------------------
try:
    nlp = spacy.load("en_core_web_trf")
except OSError:
    # Fallback to smaller model if transformer not installed
    try:
        nlp = spacy.load("en_core_web_lg")
    except OSError:
        nlp = spacy.load("en_core_web_sm")
    print("[ner] WARNING: Using small spaCy model. Install en_core_web_trf for best accuracy.")

# ---------------------------------------------------------------------------
# Custom EntityRuler patterns for legal domain
# ---------------------------------------------------------------------------
ruler = nlp.add_pipe("entity_ruler", before="ner")

LEGAL_PATTERNS = [
    # PARTY patterns
    {"label": "PARTY", "pattern": [{"TEXT": {"REGEX": r"^[A-Z][a-z]+"}, "OP": "+"}, {"LOWER": {"IN": ["inc", "llc", "ltd", "corp", "corporation", "limited", "lp", "llp"]}}]},
    {"label": "PARTY", "pattern": [{"TEXT": {"REGEX": r"^[A-Z][a-z]+"}, "OP": "+"}, {"TEXT": ",", "OP": "?"}, {"LOWER": {"IN": ["inc.", "llc.", "ltd.", "corp."]}}]},

    # JURISDICTION
    {"label": "JURISDICTION", "pattern": [{"LOWER": "state"}, {"LOWER": "of"}, {"IS_TITLE": True}]},
    {"label": "JURISDICTION", "pattern": [{"LOWER": "laws"}, {"LOWER": "of"}, {"IS_TITLE": True}]},
    {"label": "JURISDICTION", "pattern": [{"LOWER": {"IN": ["delaware", "california", "new york", "texas", "england", "wales"]}}]},
    {"label": "JURISDICTION", "pattern": [{"TEXT": "New"}, {"TEXT": "York"}]},
    {"label": "JURISDICTION", "pattern": [{"TEXT": "New"}, {"TEXT": "Jersey"}]},

    # DURATION
    {"label": "DURATION", "pattern": [{"LIKE_NUM": True}, {"LOWER": {"IN": ["year", "years", "month", "months", "day", "days"]}}]},
    {"label": "DURATION", "pattern": [{"LOWER": {"IN": ["one", "two", "three", "four", "five"]}}, {"LOWER": {"IN": ["year", "years", "month", "months"]}}]},

    # PENALTY
    {"label": "PENALTY", "pattern": [{"TEXT": "$"}, {"LIKE_NUM": True}]},
    {"label": "PENALTY", "pattern": [{"LOWER": {"IN": ["liquidated", "damages", "penalty", "fine", "forfeit"]}}]},
]

ruler.add_patterns(LEGAL_PATTERNS)


# ---------------------------------------------------------------------------
# Main extraction function
# ---------------------------------------------------------------------------
def extract_entities(text: str) -> List[Dict]:
    """
    Run the spaCy pipeline on a text segment.
    Returns a list of entity dicts: {text, label, start, end}
    """
    if not text or not text.strip():
        return []

    # Truncate to spaCy's max length to avoid memory issues
    MAX_CHARS = 100_000
    doc = nlp(text[:MAX_CHARS])

    entities = []
    seen = set()

    for ent in doc.ents:
        # Deduplicate by (text, label)
        key = (ent.text.strip().lower(), ent.label_)
        if key in seen:
            continue
        seen.add(key)

        # Filter out noise (very short or purely numeric non-money)
        if len(ent.text.strip()) < 2:
            continue

        entities.append({
            "text": ent.text.strip(),
            "label": ent.label_,
            "start": ent.start_char,
            "end": ent.end_char,
        })

    return entities


def get_parties(entities: List[Dict]) -> List[str]:
    return [e["text"] for e in entities if e["label"] == "PARTY"]


def get_dates(entities: List[Dict]) -> List[str]:
    return [e["text"] for e in entities if e["label"] == "DATE"]


def get_monetary(entities: List[Dict]) -> List[str]:
    return [e["text"] for e in entities if e["label"] in ("MONEY", "PENALTY")]


def get_jurisdictions(entities: List[Dict]) -> List[str]:
    return [e["text"] for e in entities if e["label"] == "JURISDICTION"]
