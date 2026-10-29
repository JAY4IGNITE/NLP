"""Table parser for academic curriculum documents.
Extracts Semester-wise curriculum tables (I to VIII), course offerings, credits,
categories, and contact hours.
"""

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional
import fitz


@dataclass
class ParsedSemesterCourse:
    course_code: str
    course_title: str
    category: str
    level: str
    lecture_hours: int
    tutorial_hours: int
    practical_hours: int
    credits: float
    total_hours: int
    semester_num: int
    semester_roman: str
    is_elective: bool
    source_page: int
    source_doc_id: str


@dataclass
class ParsedSemester:
    semester_num: int
    semester_roman: str
    total_credits: float
    total_hours: int
    courses: List[ParsedSemesterCourse] = field(default_factory=list)
    source_page: int = 0


ROMAN_TO_INT = {
    "I": 1, "II": 2, "III": 3, "IV": 4,
    "V": 5, "VI": 6, "VII": 7, "VIII": 8
}


def clean_cell(val: Any) -> str:
    """Clean cell text from table extractor."""
    if val is None:
        return ""
    text = str(val).replace("\n", " ").strip()
    return re.sub(r"\s+", " ", text)


def parse_numeric(val: Any, default: float = 0.0) -> float:
    """Safely parse float/int from table cell."""
    s = clean_cell(val)
    match = re.search(r"[-+]?\d*\.\d+|\d+", s)
    if match:
        try:
            return float(match.group(0))
        except ValueError:
            return default
    return default


class CurriculumTableParser:
    """Parses semester curriculum tables from university PDFs."""

    def __init__(self, doc_path: Path, doc_id: str, dept_code: str):
        self.doc_path = doc_path
        self.doc_id = doc_id
        self.dept_code = dept_code

    def extract_semester_tables(self) -> List[ParsedSemester]:
        """Extract all 8 semester curriculum tables."""
        doc = fitz.open(self.doc_path)
        semesters: Dict[int, ParsedSemester] = {}

        target_pages = []
        for pno in range(min(45, len(doc))):
            text = doc[pno].get_text()
            if "SEMESTER" in text.upper() and ("MCC" in text or "Course" in text or "Credits" in text):
                target_pages.append(pno)

        for pno in target_pages:
            page = doc[pno]
            tabs = page.find_tables()
            page_text = page.get_text()

            sem_matches = list(re.finditer(r"\b([IVX]+)\s+SEMESTER\b", page_text, re.IGNORECASE))
            if not sem_matches:
                continue

            for t_idx, tab in enumerate(tabs.tables):
                rows = tab.extract()
                if not rows or len(rows) < 2:
                    continue

                sem_roman = None
                if t_idx < len(sem_matches):
                    sem_roman = sem_matches[t_idx].group(1).upper()
                else:
                    sem_roman = sem_matches[-1].group(1).upper()

                sem_num = ROMAN_TO_INT.get(sem_roman, 0)
                if sem_num == 0 or sem_num > 8:
                    continue

                if sem_num not in semesters:
                    semesters[sem_num] = ParsedSemester(
                        semester_num=sem_num,
                        semester_roman=sem_roman,
                        total_credits=0.0,
                        total_hours=0,
                        source_page=pno + 1
                    )

                for row in rows:
                    cleaned = [clean_cell(c) for c in row if c is not None]
                    row_str = " ".join(cleaned)

                    if "Total" in row_str and ("Credits" in row_str or any(c.isdigit() for c in cleaned)):
                        nums = [parse_numeric(c) for c in cleaned if parse_numeric(c) > 0]
                        if nums:
                            semesters[sem_num].total_credits = max(nums[-2:] if len(nums) >= 2 else nums)
                        continue

                    code_match = re.search(r"\b(241[A-Z]{2}[0-9]{3})\b", row_str)
                    course_code = code_match.group(1) if code_match else None

                    is_elective = False
                    if not course_code and ("Minor Stream" in row_str or "Open Elective" in row_str):
                        course_code = f"ELEC-SEM{sem_num}-{len(semesters[sem_num].courses)+1:02d}"
                        is_elective = True

                    if not course_code:
                        continue

                    title = ""
                    category = "MCC"
                    level = "FC"
                    l_hrs = 2
                    t_hrs = 0
                    p_hrs = 0
                    credits = 3.0
                    tot_hrs = 3

                    for cell in cleaned:
                        if cell in ["MCC", "MDC", "AEC", "VAC", "SEC", "MC", "PROJ", "MSC", "UEC", "MSC/UEC", "SI"]:
                            category = cell
                        elif cell in ["FC", "IC", "AC", "FC/IC", "IC/AC"]:
                            level = cell
                        elif len(cell) > 3 and not re.search(r"^241[A-Z]{2}[0-9]{3}$", cell) and not cell.isdigit():
                            if not title or len(cell) > len(title):
                                title = cell

                    if not title or title == course_code:
                        m_title = re.search(r"241[A-Z]{2}[0-9]{3}\s+([A-Za-z0-9 &,\-\(\)\+]+?)(?=\s+(?:MCC|MDC|AEC|VAC|SEC|MC|PROJ|FC|IC|AC|$))", row_str)
                        if m_title:
                            title = m_title.group(1).strip()
                        else:
                            title = f"Academic Course {course_code}"

                    title = re.sub(r"\b(?:MCC|MDC|AEC|VAC|SEC|MC|PROJ|FC|IC|AC)\b", "", title).strip()

                    nums = [parse_numeric(c) for c in cleaned if c.isdigit()]
                    if len(nums) >= 4:
                        l_hrs = int(nums[0])
                        t_hrs = int(nums[1]) if len(nums) > 1 else 0
                        p_hrs = int(nums[2]) if len(nums) > 2 else 0
                        credits = nums[-2] if len(nums) >= 5 else nums[-1]
                        tot_hrs = int(nums[-1])
                    elif len(nums) >= 2:
                        credits = nums[-2]
                        tot_hrs = int(nums[-1])
                    elif len(nums) == 1:
                        credits = nums[0]

                    course_entry = ParsedSemesterCourse(
                        course_code=course_code,
                        course_title=title,
                        category=category,
                        level=level,
                        lecture_hours=l_hrs,
                        tutorial_hours=t_hrs,
                        practical_hours=p_hrs,
                        credits=credits,
                        total_hours=tot_hrs,
                        semester_num=sem_num,
                        semester_roman=sem_roman,
                        is_elective=is_elective,
                        source_page=pno + 1,
                        source_doc_id=self.doc_id
                    )
                    semesters[sem_num].courses.append(course_entry)

        doc.close()

        for s in semesters.values():
            if s.total_credits == 0.0 and s.courses:
                s.total_credits = sum(c.credits for c in s.courses)

        return sorted(list(semesters.values()), key=lambda x: x.semester_num)
