"""
pipeline/classifier.py
──────────────────────
Maps each segmented clause to a CUAD (Contract Understanding Atticus Dataset)
category and assigns a risk score: low / medium / high.

Categories are detected via keyword heuristics + optional LLM refinement.
"""

import re
from typing import List, Dict

# ---------------------------------------------------------------------------
# CUAD Category Definitions
# Each category has: keywords that signal its presence, base risk level.
# ---------------------------------------------------------------------------
CUAD_CATEGORIES = {
    "Definitions": {
        "keywords": ["means", "defined as", "refers to", "hereinafter", "the term"],
        "base_risk": "low",
    },
    "Term / Duration": {
        "keywords": ["term", "duration", "commencing", "effective date", "expiration", "termination date"],
        "base_risk": "low",
    },
    "Termination": {
        "keywords": ["terminate", "termination", "notice of termination", "cancel", "wind down"],
        "base_risk": "medium",
    },
    "Confidentiality / NDA": {
        "keywords": ["confidential", "non-disclosure", "nda", "proprietary", "trade secret", "disclose"],
        "base_risk": "medium",
    },
    "Intellectual Property": {
        "keywords": ["intellectual property", "ip", "patent", "copyright", "trademark", "ownership", "work for hire"],
        "base_risk": "medium",
    },
    "Non-Compete": {
        "keywords": ["non-compete", "non compete", "competitive activity", "restrain", "restrict business"],
        "base_risk": "high",
    },
    "Non-Solicitation": {
        "keywords": ["non-solicitation", "solicit", "poach", "recruit employees"],
        "base_risk": "high",
    },
    "Liability Cap": {
        "keywords": ["liability", "limit of liability", "cap on damages", "maximum liability", "aggregate liability"],
        "base_risk": "high",
    },
    "Indemnification": {
        "keywords": ["indemnif", "hold harmless", "defend", "indemnity"],
        "base_risk": "high",
    },
    "Dispute Resolution": {
        "keywords": ["arbitration", "dispute", "mediation", "litigation", "jurisdiction", "governing law"],
        "base_risk": "medium",
    },
    "Payment Terms": {
        "keywords": ["payment", "invoice", "fee", "compensation", "salary", "royalty", "price"],
        "base_risk": "low",
    },
    "Force Majeure": {
        "keywords": ["force majeure", "act of god", "unforeseen", "pandemic", "natural disaster"],
        "base_risk": "low",
    },
    "Assignment": {
        "keywords": ["assign", "transfer rights", "successor", "delegate"],
        "base_risk": "medium",
    },
    "Warranties / Representations": {
        "keywords": ["warrant", "represent", "guarantee", "as-is", "no warranty"],
        "base_risk": "medium",
    },
    "Governing Law": {
        "keywords": ["governed by", "laws of", "jurisdiction of", "applicable law"],
        "base_risk": "low",
    },
    "Penalty / Liquidated Damages": {
        "keywords": ["liquidated damages", "penalty", "fine", "forfeit", "damages"],
        "base_risk": "high",
    },
}

# Risk escalation keywords — if found, bump risk level up
RISK_ESCALATORS = [
    r"\bunlimited\b",
    r"\bperpetual\b",
    r"\birrevocable\b",
    r"\bsole discretion\b",
    r"\bno recourse\b",
    r"\bwaive[sd]?\b",
    r"\bauto.?renew\b",
    r"\bexclusive\b.*\bworldwide\b",
    r"\bpenalt(y|ies)\b",
    r"\bindemnif\w+\b.*\ball\b",
]

RISK_ESCALATOR_RE = [re.compile(p, re.IGNORECASE) for p in RISK_ESCALATORS]

RISK_ORDER = {"low": 0, "medium": 1, "high": 2}
RISK_NAMES = ["low", "medium", "high"]


def detect_category(text: str) -> str:
    """Return the best-matching CUAD category for a text segment."""
    text_lower = text.lower()
    best_cat = "General"
    best_score = 0

    for cat, info in CUAD_CATEGORIES.items():
        score = sum(1 for kw in info["keywords"] if kw.lower() in text_lower)
        if score > best_score:
            best_score = score
            best_cat = cat

    return best_cat


def compute_risk(text: str, base_risk: str) -> str:
    """Escalate risk if high-risk language is found in the clause text."""
    risk_level = RISK_ORDER[base_risk]

    for pattern in RISK_ESCALATOR_RE:
        if pattern.search(text):
            risk_level = min(risk_level + 1, 2)

    return RISK_NAMES[risk_level]


def score_risk(text: str, category: str) -> str:
    base = CUAD_CATEGORIES.get(category, {}).get("base_risk", "low")
    return compute_risk(text, base)


def classify_clauses(segments: List[Dict]) -> List[Dict]:
    """
    For each segment, detect CUAD category + risk score.
    Adds 'category' and 'risk' keys to each segment dict.
    """
    for seg in segments:
        text = seg.get("text", "")
        cat = detect_category(text)
        risk = score_risk(text, cat)

        seg["category"] = cat
        seg["risk"] = risk
        seg["risk_flags"] = _collect_flags(text)

    return segments


def _collect_flags(text: str) -> List[str]:
    """Return list of human-readable flags for why risk was escalated."""
    flags = []
    flag_map = {
        r"\bunlimited\b": "Unlimited liability exposure",
        r"\bperpetual\b": "Perpetual obligation",
        r"\birrevocable\b": "Irrevocable clause",
        r"\bsole discretion\b": "Sole discretion clause",
        r"\bno recourse\b": "No recourse provision",
        r"\bwaive[sd]?\b": "Rights waiver detected",
        r"\bauto.?renew\b": "Auto-renewal clause",
        r"\bpenalt(y|ies)\b": "Penalty clause",
        r"\bindemnif\w+\b.*\ball\b": "Broad indemnification",
    }
    for pattern, label in flag_map.items():
        if re.search(pattern, text, re.IGNORECASE):
            flags.append(label)
    return flags
