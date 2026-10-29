"""Official Academic Regulations & Institutional Policies Knowledge Base.
Grounded directly in Aditya University Autonomous B.Tech Academic Regulations 2024 (Version 3.0 / R24).
"""

from typing import Any, Dict, List, Optional

REGULATION_KNOWLEDGE: Dict[str, Dict[str, Any]] = {
    "attendance_policy": {
        "title": "Attendance & Condonation Regulations (Academic Regulation 2024 - Version 3.0)",
        "source_doc_id": "DOC-REG-2024",
        "page": 12,
        "keywords": ["attendance", "condonation", "shortage", "detention", "detained", "medical certificate", "75%", "65%"],
        "content": (
            "**Aditya University B.Tech Academic Regulations 2024 (Version 3.0) - Attendance & Condonation Rules:**\n\n"
            "- **Minimum Attendance Requirement:** A student must secure a minimum of **75% aggregate attendance** in all prescribed theory and laboratory courses in a semester to be eligible to appear for the Semester End Examinations (SEE).\n"
            "- **Condonation of Shortage:** Condonation of attendance shortage up to **10%** (i.e., attendance between **65% and 74.99%**) may be granted by the Academic Council / Principal on genuine medical grounds (accompanied by valid medical certificates) or approved participation in state/national-level sports, NCC/NSS, or university-authorized cultural events.\n"
            "- **Condonation Fee:** A prescribed university condonation fee must be paid before the declared semester deadline.\n"
            "- **Detention Policy:** Students who secure **less than 65% aggregate attendance** are **NOT eligible for condonation** under any circumstances. Such students are **detained** for shortage of attendance and must repeat the semester with the subsequent junior batch."
        )
    },
    "grading_system": {
        "title": "Grading Scale, SGPA & CGPA Calculation (Academic Regulation 2024 - Version 3.0)",
        "source_doc_id": "DOC-REG-2024",
        "page": 16,
        "keywords": ["grade", "grading", "sgpa", "cgpa", "marks", "pass marks", "grade points", "scale", "10-point", "pointer"],
        "content": (
            "**Aditya University B.Tech Academic Regulations 2024 (Version 3.0) - 10-Point Absolute Grading System:**\n\n"
            "### Letter Grade to Grade Point Mapping:\n"
            "- **Grade O (Outstanding):** Marks ≥ 90% | **10.0** Grade Points\n"
            "- **Grade A+ (Excellent):** Marks 80% to 89% | **9.0** Grade Points\n"
            "- **Grade A (Very Good):** Marks 70% to 79% | **8.0** Grade Points\n"
            "- **Grade B+ (Good):** Marks 60% to 69% | **7.0** Grade Points\n"
            "- **Grade B (Above Average):** Marks 50% to 59% | **6.0** Grade Points\n"
            "- **Grade C (Pass):** Marks 40% to 49% | **5.0** Grade Points\n"
            "- **Grade F (Fail):** Marks < 40% | **0.0** Grade Points\n"
            "- **Grade Ab (Absent):** Absent | **0.0** Grade Points\n\n"
            "### Passing Thresholds:\n"
            "- Minimum **35%** in Semester End Examination (SEE).\n"
            "- Minimum **40% in aggregate** (Continuous Internal Evaluation + Semester End Examination) to earn course credits.\n\n"
            "### Calculation Formulas:\n"
            "- **SGPA (Semester Grade Point Average):** `SUM(Course Credits * Grade Points) / SUM(Total Registered Credits)` for the semester.\n"
            "- **CGPA (Cumulative Grade Point Average):** `SUM(Course Credits * Grade Points across all completed semesters) / Total Cumulative Earned Credits`."
        )
    },
    "promotion_rules": {
        "title": "Academic Promotion & Progression Criteria (Academic Regulation 2024 - Version 3.0)",
        "source_doc_id": "DOC-REG-2024",
        "page": 19,
        "keywords": ["promotion", "credit requirement", "detained", "backlog", "progression", "eligibility", "year to year"],
        "content": (
            "**Aditya University B.Tech Academic Regulations 2024 (Version 3.0) - Promotion & Progression Rules:**\n\n"
            "- **From 1st Year to 2nd Year (Semester II to III):** A student is automatically promoted to the 2nd year provided the minimum attendance requirement (75% or 65% with condonation) is fulfilled in Semester I and II.\n"
            "- **From 2nd Year to 3rd Year (Semester IV to V):** A student must earn at least **50% of the total credits** prescribed up to Semester II (1st Year) to be eligible for promotion to the 3rd year.\n"
            "- **From 3rd Year to 4th Year (Semester VI to VII):** A student must earn at least **50% of the total credits** prescribed up to Semester IV (2nd Year) to be eligible for promotion to the 4th year.\n"
            "- **Detention for Credit Shortage:** Students failing to secure the minimum prescribed credits are detained until they clear the required backlog courses in supplementary examinations."
        )
    },
    "degree_total_credits": {
        "title": "Degree Credit Requirements (Academic Regulation 2024 - Version 3.0)",
        "source_doc_id": "DOC-REG-2024",
        "page": 8,
        "keywords": ["degree credits", "total degree credits", "credits for btech", "credits for graduation", "graduation credits", "160 credits", "120 credits", "btech total credits"],
        "content": (
            "**Aditya University B.Tech Academic Regulations 2024 (Version 3.0) - Degree Credit Framework:**\n\n"
            "- **Regular 4-Year B.Tech Program:** Total **160.0 Credits** distributed uniformly across 8 semesters (~20-23 credits per semester).\n"
            "- **Lateral Entry B.Tech Program:** Total **120.0 Credits** distributed across 6 semesters (Semesters III to VIII) for diploma/B.Sc. entry students.\n"
            "- **B.Tech (Honours / Minor):** Requires **18 to 20 additional credits** over and above the 160 degree credits, earned between Semesters IV and VIII.\n"
            "- **Mandatory Non-Credit Audit Courses:** Courses such as *Constitution of India* and *Environmental Science* must be completed with a satisfactory grade for degree award."
        )
    },
    "honours_minors": {
        "title": "B.Tech Honours & Minor Degree Regulations (Academic Regulation 2024 - Version 3.0)",
        "source_doc_id": "DOC-REG-2024",
        "page": 24,
        "keywords": ["honours", "minor", "minor degree", "honors", "extra credits", "swayam", "nptel", "specialization"],
        "content": (
            "**Aditya University B.Tech Academic Regulations 2024 (Version 3.0) - Honours & Minor Degree Guidelines:**\n\n"
            "- **Eligibility:** Students who have secured a **CGPA >= 7.50** with **NO active backlogs** at the end of Semester IV are eligible to register for B.Tech (Honours) or B.Tech with Minor.\n"
            "- **Additional Credit Requirement:** Must earn **18 to 20 additional credits** via 4-5 departmental specialization courses or approved MOOCs (SWAYAM / NPTEL) with prior department approval.\n"
            "- **B.Tech (Honours):** Advanced discipline-specific specialization within the parent department (e.g., CSE with AI/ML, Cloud Computing, or Cyber Security).\n"
            "- **B.Tech with Minor:** Interdisciplinary minor in another department (e.g., ECE student taking a Minor in CSE, or Mechanical student taking Data Science Minor)."
        )
    },
    "examination_evaluation": {
        "title": "Examination & Continuous Evaluation Scheme (Academic Regulation 2024 - Version 3.0)",
        "source_doc_id": "DOC-REG-2024",
        "page": 14,
        "keywords": ["mid exam", "cie", "see", "internal", "external", "evaluation", "marks", "revaluation", "challenge valuation"],
        "content": (
            "**Aditya University B.Tech Academic Regulations 2024 (Version 3.0) - Examination & Evaluation Scheme:**\n\n"
            "- **Theory Courses:** **30 Marks Continuous Internal Evaluation (CIE)** + **70 Marks Semester End Examination (SEE)** [or 40:60 for skill/integrated modules].\n"
            "- **CIE Components:** 2 Centralized Mid-Term Examinations + Quizzes / Assignments / Project-based assessments.\n"
            "- **Laboratory Courses:** Continuous internal lab assessment (30 marks) + External laboratory practical examination (70 marks).\n"
            "- **Re-evaluation & Challenge Valuation:** Students dissatisfied with valuation may apply for re-evaluation or script verification within 10 days of result announcement on payment of the prescribed examination fee."
        )
    },
    "institutional_leadership": {
        "title": "Aditya University Institutional Overview & Governance",
        "source_doc_id": "DOC-INST-2024",
        "page": 1,
        "keywords": ["principal", "vice chancellor", "vc", "chancellor", "sesha reddy", "location", "address", "dean", "founder", "about aditya"],
        "content": (
            "**Aditya University Institutional Profile & Leadership:**\n\n"
            "- **Institution:** Aditya University, Surampalem, East Godavari District, Andhra Pradesh, India (PIN: 533437).\n"
            "- **Chancellor:** **Dr. N. Sesha Reddy**\n"
            "- **Vice Chancellor:** Senior Academic Executive & Council Chair\n"
            "- **Status:** Autonomous State-Recognized University under UGC Act with NAAC accreditation and autonomous curricula.\n"
            "- **Contact & Administration:** Administrative Building, Aditya University Campus, Surampalem. Official Portal: https://www.adityauniversity.in/"
        )
    },
    "admission_information": {
        "title": "Aditya University B.Tech Admissions & Entrance Criteria",
        "source_doc_id": "DOC-ADM-2024",
        "page": 2,
        "keywords": ["admission", "cutoff", "eapcet", "eamcet", "college code", "eamcet code", "eapcet code", "counseling code", "admissions", "rank", "counseling", "seats"],
        "content": (
            "**Aditya University B.Tech Admissions & AP EAPCET Guidance:**\n\n"
            "- **Admission Process:** Centralized admission counseling via the **AP EAPCET** (Engineering, Agriculture and Pharmacy Common Entrance Test) organized by APSCHE, alongside Category-B institutional seats.\n"
            "- **AP EAPCET Institution Code:** `ADTP` / `ADTE`\n"
            "- **Lateral Entry:** Diploma holders qualify through **AP ECET** directly into Semester III (2nd Year).\n"
            "- **Cutoff Ranks:** Vary annually according to branch demand, applicant volume, and category quotas (OC, BC, SC, ST, EWS). CSE, CSE-Data Science, and IT typically have the highest closing rank thresholds.\n"
            "- **Admissions Office:** For seat availability and fee structure, contact the Admissions Helpdesk or visit https://www.adityauniversity.in/."
        )
    }
}


def find_regulation_match(
    query: str,
    intent: Optional[str] = None,
    entities: Optional[Dict[str, Any]] = None
) -> Optional[Dict[str, Any]]:
    """Match student queries against official institutional regulations."""
    q_lower = query.lower()
    entities = entities or {}

    # If asking about a specific course (course code, credits, syllabus, prerequisites), don't hijack with regulations
    if (entities.get("course") or entities.get("course_code")) and intent in [
        "course_code", "course_credits", "course_ltpc", "unit_syllabus", "full_syllabus", "course_prerequisites"
    ]:
        return None

    has_semester = (
        entities.get("semester") is not None
        or any(k in q_lower for k in [
            "semester", "sem 1", "sem 2", "sem 3", "sem 4", "sem 5", "sem 6", "sem 7", "sem 8",
            "1st sem", "2nd sem", "3rd sem", "4th sem", "5th sem", "6th sem", "7th sem", "8th sem"
        ])
    )

    # If asking about specific semester courses/credits, do not hijack with general degree regulations
    if has_semester and intent in ["semester_subjects", "semester_total_credits"]:
        return None

    # Direct intent mapping
    if intent in REGULATION_KNOWLEDGE:
        if intent == "degree_total_credits" and has_semester:
            return None
        item = REGULATION_KNOWLEDGE[intent]
        return {
            "chunk_id": f"SQL-REG-{intent.upper()}",
            "text": item["content"],
            "content": item["content"],
            "title": item["title"],
            "source_document_id": item["source_doc_id"],
            "source_document": item["source_doc_id"],
            "page_number": item["page"],
            "source_page": item["page"],
            "retrieval_score": 1.0,
            "department_code": "University"
        }

    # Keyword and topic matching
    for reg_key, item in REGULATION_KNOWLEDGE.items():
        if reg_key == "degree_total_credits" and has_semester:
            continue
        if any(kw in q_lower for kw in item["keywords"]):
            return {
                "chunk_id": f"SQL-REG-{reg_key.upper()}",
                "text": item["content"],
                "content": item["content"],
                "title": item["title"],
                "source_document_id": item["source_doc_id"],
                "source_document": item["source_doc_id"],
                "page_number": item["page"],
                "source_page": item["page"],
                "retrieval_score": 1.0,
                "department_code": "University"
            }

    return None
