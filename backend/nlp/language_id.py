"""Language identification module.
Detects English ('en'), Telugu script ('te'), and Romanized Telugu ('te-en')
for student academic inquiries.
"""

import re
from typing import Tuple

TELUGU_RANGE_START = 0x0C00
TELUGU_RANGE_END = 0x0C7F

ROMANIZED_TELUGU_PATTERNS = [
    r"\benni\b",
    r"\bcheppandi\b",
    r"\bivvandi\b",
    r"\bemiti\b",
    r"\bunna\b",
    r"\bundhi?\b",
    r"\bchala\b",
    r"\bnamaskaram\b",
    r"\bsubjects\s+list\s+(?:cheppandi|ivvandi)\b",
    r"\bcredits\s+enni\b",
    r"\bsem(?:ester)?\s+lo\b"
]


def identify_language(text: str) -> Tuple[str, float]:
    """Detect whether query is English ('en'), Telugu script ('te'), or Romanized Telugu ('te-en').
    Returns: (language_code, confidence)
    """
    if not text:
        return "en", 1.0

    lower = text.lower().strip()

    # 1. Check for Telugu script characters
    telugu_chars = sum(1 for char in text if TELUGU_RANGE_START <= ord(char) <= TELUGU_RANGE_END)
    total_alpha = sum(1 for char in text if char.isalpha())

    if total_alpha > 0 and (telugu_chars / total_alpha) > 0.15:
        telugu_ratio = telugu_chars / total_alpha
        return "te", round(min(1.0, 0.7 + telugu_ratio * 0.3), 2)

    # 2. Check for Romanized Telugu keywords
    for pat in ROMANIZED_TELUGU_PATTERNS:
        if re.search(pat, lower):
            return "te-en", 0.95

    return "en", 1.0
