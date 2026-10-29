"""Structure parser for extracting detailed course syllabi, unit breakdowns,
course outcomes, and textbook/reference records from university curriculum documents.
"""

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional
import fitz


@dataclass
class ParsedUnit:
    unit_number: int
    unit_roman: str
    title: str
    content: str
    practice_content: Optional[str]
    source_page: int


@dataclass
class ParsedTextbook:
    book_type: str
    title: str
    authors: Optional[str]
    publisher: Optional[str]
    edition: Optional[str]
    isbn: Optional[str]
    raw_text: str


@dataclass
class ParsedCourseSyllabus:
    course_code: str
    course_title: str
    department_code: str
    curriculum_version: str
    credits: float
    lecture_hours: int
    tutorial_hours: int
    practical_hours: int
    common_to: Optional[str]
    outcomes: List[Dict[str, str]] = field(default_factory=list)
    units: List[ParsedUnit] = field(default_factory=list)
    textbooks: List[ParsedTextbook] = field(default_factory=list)
    source_page: int = 0
    source_doc_id: str = ""


ROMAN_TO_NUM = {"I": 1, "II": 2, "III": 3, "IV": 4, "V": 5, "VI": 6}


class SyllabusStructureParser:
    """Parses course syllabus sections, extracting outcomes, units, and books."""

    def __init__(self, doc_path: Path, doc_id: str, dept_code: str, version: str = "Version 3.0"):
        self.doc_path = doc_path
        self.doc_id = doc_id
        self.dept_code = dept_code
        self.version = version

    def parse_all_syllabi(self, max_pages: Optional[int] = None) -> List[ParsedCourseSyllabus]:
        """Scan document pages and parse all course syllabi."""
        doc = fitz.open(self.doc_path)
        total_pages = len(doc) if max_pages is None else min(max_pages, len(doc))

        courses: List[ParsedCourseSyllabus] = []
        current_course: Optional[ParsedCourseSyllabus] = None

        for pno in range(total_pages):
            text = doc[pno].get_text()
            if not text.strip():
                continue

            code_match = re.search(r"Course\s*Code\s*[:\-]?\s*(241[A-Z]{2}[0-9]{3})", text, re.IGNORECASE)

            if code_match:
                if current_course and (current_course.units or current_course.outcomes):
                    courses.append(current_course)

                code = code_match.group(1).upper()
                lines = [l.strip() for l in text.splitlines() if l.strip()]
                title = ""
                common_to = None

                for idx, line in enumerate(lines):
                    if "(Common to" in line or "(common to" in line:
                        common_to = line
                        if idx > 0 and not lines[idx-1].startswith("B.Tech") and not lines[idx-1].startswith("Page"):
                            title = lines[idx-1]
                        break
                    elif code in line:
                        for prev_idx in range(idx - 1, max(-1, idx - 4), -1):
                            prev_line = lines[prev_idx]
                            if not prev_line.startswith("B.Tech") and "Curriculum" not in prev_line and "Page" not in prev_line:
                                if not title:
                                    title = prev_line
                                    break

                if not title:
                    title = f"Course {code}"

                l_hrs, t_hrs, p_hrs, credits = 2, 0, 0, 3.0
                ltpc_match = re.search(r"L\s+T\s+P\s+C\s*\n[^\n]*\n\s*(\d+)\s+(\d+)\s+(\d+)\s+(\d+)", text)
                if not ltpc_match:
                    ltpc_match = re.search(r"(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s*\n\s*Course Outcomes", text)

                if ltpc_match:
                    l_hrs = int(ltpc_match.group(1))
                    t_hrs = int(ltpc_match.group(2))
                    p_hrs = int(ltpc_match.group(3))
                    credits = float(ltpc_match.group(4))

                current_course = ParsedCourseSyllabus(
                    course_code=code,
                    course_title=title,
                    department_code=self.dept_code,
                    curriculum_version=self.version,
                    credits=credits,
                    lecture_hours=l_hrs,
                    tutorial_hours=t_hrs,
                    practical_hours=p_hrs,
                    common_to=common_to,
                    source_page=pno + 1,
                    source_doc_id=self.doc_id,
                )

            if current_course:
                co_matches = re.findall(r"(CO\d+)\s*[:\-]?\s*([^\n]+(?:\n(?!\s*(?:CO\d+|UNIT|Mapping))[^\n]+)*)", text)
                for co_code, desc in co_matches:
                    clean_desc = re.sub(r"\s+", " ", desc).strip()
                    if not any(o["code"] == co_code for o in current_course.outcomes):
                        current_course.outcomes.append({"code": co_code, "description": clean_desc})

                unit_splits = list(re.finditer(r"(UNIT\s*[\-–—]\s*([IVX]+))\s*\n([^\n]+)?", text))
                for idx, match in enumerate(unit_splits):
                    unit_roman_raw = match.group(1)
                    roman_num = match.group(2).upper()
                    unit_num = ROMAN_TO_NUM.get(roman_num, len(current_course.units) + 1)
                    unit_title = (match.group(3) or "").strip()

                    start_pos = match.end()
                    end_pos = unit_splits[idx + 1].start() if idx + 1 < len(unit_splits) else len(text)
                    unit_raw_text = text[start_pos:end_pos]

                    for stop_kw in ["Text Books:", "TEXT BOOKS", "Mapping of", "Reference Books:"]:
                        if stop_kw in unit_raw_text:
                            unit_raw_text = unit_raw_text.split(stop_kw)[0]

                    practice = None
                    if "Practice(" in unit_raw_text or "Practice:" in unit_raw_text:
                        parts = re.split(r"Practice(?:\([^\)]*\))?:\s*", unit_raw_text, maxsplit=1)
                        content = parts[0].strip()
                        practice = parts[1].strip() if len(parts) > 1 else None
                    else:
                        content = unit_raw_text.strip()

                    content = re.sub(r"\s+", " ", content)

                    if not any(u.unit_number == unit_num for u in current_course.units):
                        current_course.units.append(ParsedUnit(
                            unit_number=unit_num,
                            unit_roman=f"UNIT - {roman_num}",
                            title=unit_title,
                            content=content,
                            practice_content=practice,
                            source_page=pno + 1
                        ))

                tb_section = re.search(r"Text\s*Books?:\s*\n([\s\S]*?)(?:Reference\s*Books?:|Mapping\s*of|Web\s*Resources:|$)", text, re.IGNORECASE)
                if tb_section:
                    tb_lines = [l.strip() for l in tb_section.group(1).splitlines() if l.strip()]
                    current_tb = ""
                    for line in tb_lines:
                        if re.match(r"^\d+\b", line):
                            if current_tb:
                                current_course.textbooks.append(ParsedTextbook(
                                    book_type="Textbook",
                                    title=current_tb,
                                    authors=None,
                                    publisher=None,
                                    edition=None,
                                    isbn=None,
                                    raw_text=current_tb
                                ))
                            current_tb = re.sub(r"^\d+\s*", "", line)
                        else:
                            current_tb += " " + line
                    if current_tb:
                        current_course.textbooks.append(ParsedTextbook(
                            book_type="Textbook",
                            title=current_tb,
                            authors=None,
                            publisher=None,
                            edition=None,
                            isbn=None,
                            raw_text=current_tb
                        ))

                ref_section = re.search(r"Reference\s*Books?:\s*\n([\s\S]*?)(?:Mapping\s*of|Web\s*Resources:|$)", text, re.IGNORECASE)
                if ref_section:
                    ref_lines = [l.strip() for l in ref_section.group(1).splitlines() if l.strip()]
                    current_ref = ""
                    for line in ref_lines:
                        if re.match(r"^\d+\b", line):
                            if current_ref:
                                current_course.textbooks.append(ParsedTextbook(
                                    book_type="Reference",
                                    title=current_ref,
                                    authors=None,
                                    publisher=None,
                                    edition=None,
                                    isbn=None,
                                    raw_text=current_ref
                                ))
                            current_ref = re.sub(r"^\d+\s*", "", line)
                        else:
                            current_ref += " " + line
                    if current_ref:
                        current_course.textbooks.append(ParsedTextbook(
                            book_type="Reference",
                            title=current_ref,
                            authors=None,
                            publisher=None,
                            edition=None,
                            isbn=None,
                            raw_text=current_ref
                        ))

        if current_course and (current_course.units or current_course.outcomes):
            courses.append(current_course)

        doc.close()
        return courses
