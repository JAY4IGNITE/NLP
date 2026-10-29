"""Hybrid Entity Extraction Engine.
Combines dictionary lookup, regex pattern matching, string normalization, and fuzzy matching.
Extracts: course, canonical_course_name, course_code, branch/department, semester, unit.
"""

import difflib
import json
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from backend.config import DATA_DIR, STRUCTURED_DIR
from backend.nlp.normalizer import DEPARTMENT_ALIASES, normalize_query, COMMON_COURSE_ABBREVIATIONS

ROMAN_NUMERALS = {
    "i": 1, "ii": 2, "iii": 3, "iv": 4, "v": 5, "vi": 6, "vii": 7, "viii": 8
}

WORD_NUMBERS = {
    "first": 1, "second": 2, "third": 3, "fourth": 4, "fifth": 5,
    "sixth": 6, "seventh": 7, "eighth": 8, "one": 1, "two": 2, "three": 3, "four": 4, "five": 5
}

DEPT_PATTERNS = {
    "cse-ds": "CSE-DS",
    "data science": "CSE-DS",
    "cse": "CSE",
    "computer science": "CSE",
    "ece": "ECE",
    "electronics": "ECE",
    "eee": "EEE",
    "electrical": "EEE",
    "it": "IT",
    "information technology": "IT",
    "civil": "CE",
    "ce": "CE",
    "mining": "MIN",
    "min": "MIN",
    "petroleum": "PT",
    "pt": "PT",
}

KNOWN_COURSES = [
    "Linear algebra & Calculus", "Applied Chemistry", "Programming for Problem Solving Using C",
    "IT & AI Skills", "Basic Electrical & Electronics Engineering", "Essential Cognitive Skills",
    "Universal Human Values", "Indian Cultural Heritage", "Differential equations &vector calculus",
    "Modern Physics", "Data Structures", "Engineering Graphics", "Engineering Workshop",
    "Digital Logic & Computer Organization", "Design Thinking", "Sports & Yoga", "Environmental Science",
    "Discrete Mathematics", "Object Oriented Programming through C++", "Theory of Computation",
    "Database Management Systems", "Agile Software Engineering", "Data Analysis using Python",
    "Constitution of India", "Probability & Statistics", "Java Programming", "Operating Systems",
    "Artificial Intelligence", "Advanced Data Structures & Algorithm Analysis", "Computer Networks",
    "Compiler Design", "Machine Learning", "Bigdata Analytics", "Data Mining",
    "Cryptography & Network Security", "Software Architecture", "Internet of Things"
]


class AcademicEntityExtractor:
    """Enterprise hybrid rule, dictionary, regex, and fuzzy entity extractor."""

    def __init__(self, courses_file: Optional[Path] = None):
        self.courses_file = Path(courses_file) if courses_file else (STRUCTURED_DIR / "courses.json")
        self.courses_db: List[Dict[str, Any]] = []
        self.alias_to_course: Dict[str, Dict[str, Any]] = {}
        self.code_to_course: Dict[str, Dict[str, Any]] = {}
        self.all_alias_strings: List[str] = []
        self.load_courses()

    def load_courses(self):
        """Load structured courses if available or populate from KNOWN_COURSES."""
        if self.courses_file.exists():
            try:
                with open(self.courses_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                self.courses_db = data.get("courses", [])
                for c in self.courses_db:
                    code_norm = c["course_code"].upper().replace(" ", "").replace("-", "")
                    self.code_to_course[code_norm] = c
                    for variant in [c["course_name"], c["course_name"].replace("&", "and"), c["course_name"].replace("and", "&")]:
                        v_norm = variant.lower().strip()
                        self.alias_to_course[v_norm] = c
                        self.all_alias_strings.append(v_norm)
                    self.alias_to_course[c["course_code"].lower()] = c
                    self.all_alias_strings.append(c["course_code"].lower())
                    for a in c.get("aliases", []):
                        a_norm = a.lower().strip()
                        self.alias_to_course[a_norm] = c
                        self.all_alias_strings.append(a_norm)
            except Exception:
                pass

        # Ingest all courses from live database if available
        try:
            from backend.database.connection import SessionLocal
            from backend.database.models import Course
            db = SessionLocal()
            for c in db.query(Course).all():
                c_norm = c.code.upper().replace(" ", "").replace("-", "")
                obj = {"course_name": c.title, "course_code": c.code, "aliases": [c.code]}
                self.code_to_course[c_norm] = obj
                for v in [c.title, c.title.replace("&", "and"), c.title.replace("and", "&")]:
                    vl = v.lower().strip()
                    self.alias_to_course[vl] = obj
                    self.all_alias_strings.append(vl)
                self.alias_to_course[c.code.lower()] = obj
                self.all_alias_strings.append(c.code.lower())
            db.close()
        except Exception:
            pass

        # Also add known canonical names and common abbreviations
        for c_name in KNOWN_COURSES:
            for variant in [c_name, c_name.replace("&", "and"), c_name.replace("and", "&")]:
                c_lower = variant.lower().strip()
                if c_lower not in self.alias_to_course:
                    obj = {"course_name": c_name, "course_code": "", "aliases": []}
                    self.alias_to_course[c_lower] = obj
                    self.all_alias_strings.append(c_lower)

        for abbr, full in COMMON_COURSE_ABBREVIATIONS.items():
            if abbr not in self.alias_to_course:
                obj = {"course_name": full, "course_code": "", "aliases": [abbr]}
                self.alias_to_course[abbr] = obj
                self.all_alias_strings.append(abbr)

        self.all_alias_strings = sorted(list(set(self.all_alias_strings)), key=len, reverse=True)

    def extract_entities(self, text: str) -> Dict[str, Any]:
        """Extract all curriculum slots and entities from query."""
        if not text:
            return {
                "course": None,
                "canonical_course_name": None,
                "course_code": None,
                "branch": None,
                "department": None,
                "semester": None,
                "unit": None
            }

        normalized = normalize_query(text)
        lower = normalized.lower()
        entities: Dict[str, Any] = {}

        # 1. Course Code (Aditya 241[A-Z]{2}[0-9]{3} or standard [A-Z]{2,3}[0-9]{3})
        code_match = re.search(r"\b(241[A-Z]{2}[0-9]{3})\b", normalized)
        if code_match:
            entities["course_code"] = code_match.group(1).upper()
            entities["course"] = code_match.group(1).upper()
        else:
            short_code_match = re.search(r"\b([A-Za-z]{2,3})\s*[-]?\s*(\d{3})\b", text)
            if short_code_match:
                raw_code = f"{short_code_match.group(1).upper()}{short_code_match.group(2)}"
                if raw_code in self.code_to_course:
                    entities["course_code"] = raw_code
                    entities["course"] = raw_code

        # 2. Semester Number
        sem_match = re.search(r"\b(?:semester|sem)\s*[-]?\s*([1-8]|i{1,3}|iv|v|vi{1,3}|viii)\b", lower)
        if sem_match:
            val = sem_match.group(1)
            entities["semester"] = int(val) if val.isdigit() else ROMAN_NUMERALS.get(val)
        else:
            ord_match = re.search(r"\b(1st|2nd|3rd|4th|5th|6th|7th|8th|first|second|third|fourth|fifth|sixth|seventh|eighth)[\s\-]+(?:semester|sem)\b", lower)
            if ord_match:
                v = ord_match.group(1)
                entities["semester"] = int(v[0]) if v[0].isdigit() else WORD_NUMBERS.get(v)

        # 3. Unit Number
        unit_match = re.search(r"\b(?:unit|module)\s*[-]?\s*([1-5]|i{1,3}|iv|v)\b", lower)
        if unit_match:
            val = unit_match.group(1)
            entities["unit"] = int(val) if val.isdigit() else ROMAN_NUMERALS.get(val)
        else:
            unit_ord = re.search(r"\b(1st|2nd|3rd|4th|5th|first|second|third|fourth|fifth)[\s\-]+(?:unit|module)\b", lower)
            if unit_ord:
                v = unit_ord.group(1)
                entities["unit"] = int(v[0]) if v[0].isdigit() else WORD_NUMBERS.get(v)

        # 4. Department / Branch Extraction
        comp_match = re.search(r"(?:compare|between)\s+([A-Za-z\s]+?)\s+(?:and|with|to)\s+([A-Za-z\s]+)", lower)
        if comp_match:
            d1 = self._resolve_dept(comp_match.group(1).strip())
            d2 = self._resolve_dept(comp_match.group(2).strip())
            if d1:
                entities["department"] = d1
                entities["branch"] = d1
            if d2:
                entities["department_b"] = d2

        if "department" not in entities:
            for alias, code in DEPT_PATTERNS.items():
                if re.search(rf"\b{re.escape(alias)}\b", lower):
                    entities["department"] = code
                    entities["branch"] = code
                    break

        # 5. Course Name extraction (if not already extracted by code)
        if "course" not in entities or not entities.get("canonical_course_name"):
            matched_obj = None
            matched_alias = None

            for alias in self.all_alias_strings:
                if len(alias) <= 4:
                    pattern = rf"\b{re.escape(alias)}\b"
                else:
                    pattern = rf"{re.escape(alias)}"

                if re.search(pattern, lower):
                    matched_obj = self.alias_to_course[alias]
                    matched_alias = alias
                    break

            if not matched_obj:
                words = [w for w in re.findall(r"\b[a-zA-Z]{3,}\b", lower) if w not in {"what", "which", "give", "tell", "explain", "semester", "topics", "syllabus", "credits", "prerequisites"}]
                for word in words:
                    close = difflib.get_close_matches(word, self.all_alias_strings, n=1, cutoff=0.82)
                    if close:
                        matched_alias = close[0]
                        matched_obj = self.alias_to_course[matched_alias]
                        break

            if matched_obj:
                entities["canonical_course_name"] = matched_obj.get("course_name")
                if "course" not in entities or not entities["course"]:
                    entities["course"] = matched_obj.get("course_name") or matched_alias
                if not entities.get("course_code") and matched_obj.get("course_code"):
                    entities["course_code"] = matched_obj["course_code"]

        # Ambiguity detection for "DS"
        if re.search(r"\bds\b", text.lower()):
            if "course" not in entities or entities.get("course") in ["Data Structures", "Computer Science and Engineering (Data Science)"]:
                entities["is_ambiguous"] = True
                entities["ambiguity_options"] = [
                    "Data Structures (Core Course)",
                    "Computer Science and Engineering (Data Science) (Department)"
                ]

        # Curriculum version
        if "v3" in lower or "version 3" in lower:
            entities["curriculum_version"] = "Version 3.0"
        elif "v2" in lower or "version 2" in lower:
            entities["curriculum_version"] = "Version 2.0"

        return entities

    def extract(self, query: str) -> Dict[str, Any]:
        """Convenience method matching NLP-cornerstone contract."""
        return self.extract_entities(query)

    def _resolve_dept(self, text: str) -> Optional[str]:
        for alias, code in DEPT_PATTERNS.items():
            if re.search(rf"\b{re.escape(alias)}\b", text.lower()):
                return code
        return None


entity_extractor = AcademicEntityExtractor()
AcademicEntityExtractor.entity_extractor = entity_extractor
