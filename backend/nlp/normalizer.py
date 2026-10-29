"""Query normalization module for academic inquiries.
Normalizes whitespace, course codes, department aliases, semester expressions,
unit numbers, and common abbreviations.
"""

import re
import unicodedata
from typing import Dict, Tuple

DEPARTMENT_ALIASES: Dict[str, Tuple[str, str]] = {
    "cse": ("Computer Science and Engineering", "CSE"),
    "cs": ("Computer Science and Engineering", "CSE"),
    "ds": ("Computer Science and Engineering (Data Science)", "CSE-DS"),
    "cse-ds": ("Computer Science and Engineering (Data Science)", "CSE-DS"),
    "data science": ("Computer Science and Engineering (Data Science)", "CSE-DS"),
    "ece": ("Electronics and Communication Engineering", "ECE"),
    "eee": ("Electrical and Electronics Engineering", "EEE"),
    "it": ("Information Technology", "IT"),
    "ce": ("Civil Engineering", "CE"),
    "civil": ("Civil Engineering", "CE"),
    "min": ("Mining Engineering", "MIN"),
    "mining": ("Mining Engineering", "MIN"),
    "pt": ("Petroleum Technology", "PT"),
    "petroleum": ("Petroleum Technology", "PT"),
}

COMMON_COURSE_ABBREVIATIONS: Dict[str, str] = {
    "dbms": "Database Management Systems",
    "os": "Operating Systems",
    "ml": "Machine Learning",
    "ai": "Artificial Intelligence",
    "cn": "Computer Networks",
    "cd": "Compiler Design",
    "toc": "Theory of Computation",
    "bda": "Bigdata Analytics",
    "dm": "Data Mining",
    "cns": "Cryptography & Network Security",
    "sa": "Software Architecture",
    "se": "Agile Software Engineering",
}

ROMAN_NUMS = {
    "i": "1", "ii": "2", "iii": "3", "iv": "4",
    "v": "5", "vi": "6", "vii": "7", "viii": "8"
}


def normalize_query(text: str) -> str:
    """Normalize user question text."""
    if not text:
        return ""

    # 1. Unicode NFKC
    normalized = unicodedata.normalize("NFKC", text)

    # 2. Whitespace collapse
    normalized = re.sub(r"\s+", " ", normalized).strip()

    # 3. Normalize Course Codes: '241cs001' -> '241CS001'
    def upper_code(m):
        return m.group(0).upper()
    normalized = re.sub(r"\b241[a-zA-Z]{2}[0-9]{3}\b", upper_code, normalized)

    # 4. Normalize Unit mentions: 'unit-iii', 'unit iii', '3rd unit' -> 'Unit 3'
    for r, n in ROMAN_NUMS.items():
        normalized = re.sub(rf"\bunit[\s\-]+{r}\b", f"Unit {n}", normalized, flags=re.IGNORECASE)
    normalized = re.sub(r"\b(\d+)(?:st|nd|rd|th)\s+unit\b", r"Unit \1", normalized, flags=re.IGNORECASE)

    # 5. Normalize Semester mentions: 'sem 5', '5th sem', 'semester v' -> 'Semester 5'
    for r, n in ROMAN_NUMS.items():
        normalized = re.sub(rf"\bsem(?:ester)?[\s\-]+{r}\b", f"Semester {n}", normalized, flags=re.IGNORECASE)
    normalized = re.sub(r"\bsem(?:ester)?[\s\-]+(\d)\b", r"Semester \1", normalized, flags=re.IGNORECASE)
    normalized = re.sub(r"\b(\d+)(?:st|nd|rd|th)\s+sem(?:ester)?\b", r"Semester \1", normalized, flags=re.IGNORECASE)

    # 6. Expand unambiguous acronyms in context
    for abbr, full in COMMON_COURSE_ABBREVIATIONS.items():
        normalized = re.sub(rf"\b{abbr}\b", full, normalized, flags=re.IGNORECASE)

    return normalized
