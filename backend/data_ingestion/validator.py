"""Academic record validator and conflict detection engine.
Audits extracted curriculum records, detects cross-department discrepancies,
validates course code formats, credit ranges, and semester structures.
"""

import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from backend.database.connection import SessionLocal
from backend.database.models import ExtractionIssue


@dataclass
class ValidationReport:
    total_courses_checked: int = 0
    valid_courses: int = 0
    format_errors: int = 0
    credit_anomalies: int = 0
    conflicts_detected: int = 0
    issues: List[Dict[str, Any]] = field(default_factory=list)


COURSE_CODE_PATTERN = re.compile(r"^241[A-Z]{2}[0-9]{3}$")


class AcademicRecordValidator:
    """Validates curriculum records and tracks discrepancies."""

    def __init__(self, db_session=None):
        self.db = db_session or SessionLocal()

    def validate_course(self, course_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Validate a single course record."""
        issues = []
        code = course_data.get("course_code", "")
        credits = course_data.get("credits", 0.0)
        title = course_data.get("course_title", "")
        doc_id = course_data.get("source_doc_id", "UNKNOWN")

        # 1. Format check
        if not COURSE_CODE_PATTERN.match(code) and not code.startswith("ELEC-"):
            issues.append({
                "doc_id": doc_id,
                "course_code": code,
                "issue_type": "invalid_code_format",
                "severity": "warning",
                "details": {"message": f"Course code '{code}' does not match standard 241[A-Z]{{2}}[0-9]{{3}} format."}
            })

        # 2. Credits check
        if credits < 0 or credits > 16:
            issues.append({
                "doc_id": doc_id,
                "course_code": code,
                "issue_type": "credit_out_of_range",
                "severity": "error",
                "details": {"message": f"Course credits {credits} outside acceptable range (0-16)."}
            })

        # 3. Missing title
        if not title or len(title.strip()) < 3:
            issues.append({
                "doc_id": doc_id,
                "course_code": code,
                "issue_type": "missing_title",
                "severity": "warning",
                "details": {"message": "Course title is missing or suspiciously short."}
            })

        return issues

    def detect_cross_department_conflicts(self, all_courses: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Compare courses across departments to find genuine conflicts."""
        grouped_by_code: Dict[str, List[Dict[str, Any]]] = {}
        for c in all_courses:
            code = c.get("course_code")
            if code and not code.startswith("ELEC-"):
                grouped_by_code.setdefault(code, []).append(c)

        conflict_issues = []
        for code, instances in grouped_by_code.items():
            if len(instances) > 1:
                credit_set = set(inst["credits"] for inst in instances)
                if len(credit_set) > 1:
                    conflict_issues.append({
                        "doc_id": instances[0].get("source_doc_id", "MULTI"),
                        "course_code": code,
                        "issue_type": "conflicting_credits",
                        "severity": "warning",
                        "details": {
                            "message": f"Course {code} has differing credits across departments: {list(credit_set)}",
                            "instances": [
                                {"dept": i.get("department_code"), "credits": i.get("credits"), "doc": i.get("source_doc_id")}
                                for i in instances
                            ]
                        }
                    })

                titles = list(set(inst["course_title"].strip().lower() for inst in instances))
                if len(titles) > 1:
                    conflict_issues.append({
                        "doc_id": instances[0].get("source_doc_id", "MULTI"),
                        "course_code": code,
                        "issue_type": "conflicting_titles",
                        "severity": "info",
                        "details": {
                            "message": f"Course {code} has slight title variations across departments.",
                            "variations": [inst["course_title"] for inst in instances]
                        }
                    })

        return conflict_issues

    def persist_issues(self, issues: List[Dict[str, Any]]) -> None:
        """Save detected issues into the database."""
        try:
            for item in issues:
                issue_obj = ExtractionIssue(
                    doc_id=item.get("doc_id", "SYSTEM"),
                    issue_type=item.get("issue_type", "general"),
                    severity=item.get("severity", "warning"),
                    course_code=item.get("course_code"),
                    details=item.get("details"),
                    status="pending_review",
                )
                self.db.add(issue_obj)
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            print(f"Error persisting issues: {e}")
        finally:
            self.db.close()
