"""Taxonomy definition for Hierarchical Intent Recognition.
Defines Domain -> Detailed Intent -> Entity Slot mappings.
"""

from typing import Dict, List, Set

DOMAINS = [
    "curriculum",
    "syllabus",
    "electives",
    "examinations",
    "internships",
    "administration",
    "campus_support"
]

INTENT_TAXONOMY: Dict[str, Dict[str, any]] = {
    # 1. Curriculum Domain
    "course_credits": {
        "domain": "curriculum",
        "description": "Inquire about credit count or L-T-P breakdown of a course",
        "slots": ["course", "department"]
    },
    "course_code": {
        "domain": "curriculum",
        "description": "Inquire about the official alphanumeric course code of a subject",
        "slots": ["course", "department"]
    },
    "course_category": {
        "domain": "curriculum",
        "description": "Inquire about course category (MCC, MDC, AEC, VAC, SEC, MC)",
        "slots": ["course", "department"]
    },
    "course_prerequisites": {
        "domain": "curriculum",
        "description": "Inquire about prerequisites required before taking a course",
        "slots": ["course", "department"]
    },
    "course_ltpc": {
        "domain": "curriculum",
        "description": "Inquire about lecture, tutorial, practical hours, and total contact hours",
        "slots": ["course"]
    },
    "semester_subjects": {
        "domain": "curriculum",
        "description": "List all subjects, laboratories, and courses offered in a specific semester",
        "slots": ["semester", "department"]
    },
    "semester_total_credits": {
        "domain": "curriculum",
        "description": "Inquire about total credits assigned to a semester",
        "slots": ["semester", "department"]
    },
    "degree_total_credits": {
        "domain": "curriculum",
        "description": "Inquire about total credits required for B.Tech degree completion (160 credits)",
        "slots": ["department"]
    },
    "curriculum_version": {
        "domain": "curriculum",
        "description": "Inquire about active curriculum version (Version 3.0) or admission batch",
        "slots": ["department", "curriculum_version"]
    },
    "course_comparison": {
        "domain": "curriculum",
        "description": "Compare courses or semester curricula between two departments",
        "slots": ["semester", "department", "department_b"]
    },

    # 2. Syllabus and Learning Domain
    "unit_syllabus": {
        "domain": "syllabus",
        "description": "Explain or summarize a specific unit of a course syllabus",
        "slots": ["course", "unit"]
    },
    "full_syllabus": {
        "domain": "syllabus",
        "description": "Retrieve comprehensive multi-unit syllabus for a course",
        "slots": ["course"]
    },
    "course_outcomes": {
        "domain": "syllabus",
        "description": "Inquire about course outcomes (COs) and graduate attributes",
        "slots": ["course"]
    },
    "textbook_references": {
        "domain": "syllabus",
        "description": "Inquire about recommended textbooks, reference books, and authors",
        "slots": ["course"]
    },
    "lab_experiments": {
        "domain": "syllabus",
        "description": "Inquire about practical lab experiments or software practice modules",
        "slots": ["course"]
    },

    # 3. Electives and Specializations Domain
    "minor_stream_list": {
        "domain": "electives",
        "description": "List minor streams and specializations available to a department",
        "slots": ["department"]
    },
    "minor_stream_courses": {
        "domain": "electives",
        "description": "List specific courses under a minor stream or degree",
        "slots": ["minor_stream", "department"]
    },
    "elective_options": {
        "domain": "electives",
        "description": "Inquire about university open electives (UEC) or department electives",
        "slots": ["department", "semester"]
    },

    # 4. Examinations Domain
    "academic_calendar": {
        "domain": "examinations",
        "description": "Inquire about academic schedule, working days, or semester start dates",
        "slots": ["academic_year", "semester"]
    },
    "exam_timetable": {
        "domain": "examinations",
        "description": "Inquire about examination schedule, dates, and mid-term assessments",
        "slots": ["semester", "examination_type"]
    },

    # 5. Internships and Placements Domain
    "internship_requirements": {
        "domain": "internships",
        "description": "Inquire about summer internships (SI) and full-semester project requirements",
        "slots": ["semester", "department"]
    },

    # 6. Administration & Regulations Domain
    "attendance_policy": {
        "domain": "administration",
        "description": "Inquire about minimum attendance (75%), condonation rules (65-75%), and detention policy",
        "slots": []
    },
    "grading_system": {
        "domain": "administration",
        "description": "Inquire about 10-point grading scale, letter grades (O to F), SGPA and CGPA calculation, and pass marks",
        "slots": []
    },
    "promotion_rules": {
        "domain": "administration",
        "description": "Inquire about year-to-year promotion criteria, 50% credit threshold, and backlog detention",
        "slots": []
    },
    "honours_minors": {
        "domain": "electives",
        "description": "Inquire about B.Tech Honours and Minor degrees, CGPA cutoff (7.50), and extra 18-20 credits",
        "slots": []
    },
    "institutional_leadership": {
        "domain": "administration",
        "description": "Inquire about Aditya University leadership, Chancellor, campus location, and governance",
        "slots": []
    },
    "admission_information": {
        "domain": "administration",
        "description": "Inquire about Aditya University admissions, AP EAPCET code, campus location, or contact",
        "slots": []
    },

    # 7. Campus Support and Conversation
    "greeting": {
        "domain": "campus_support",
        "description": "Conversational greeting or hello",
        "slots": []
    },
    "thanks": {
        "domain": "campus_support",
        "description": "User expression of gratitude",
        "slots": []
    },
    "clarification": {
        "domain": "campus_support",
        "description": "Ambiguous query requiring user clarification",
        "slots": []
    },
    "out_of_scope": {
        "domain": "campus_support",
        "description": "Questions outside Aditya University academic curriculum and helpdesk",
        "slots": []
    }
}

ACTIVE_INTENTS: List[str] = list(INTENT_TAXONOMY.keys())
