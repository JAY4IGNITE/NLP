"""Source inventory module for discovering, validating, and cataloging curriculum documents."""
import csv
import hashlib
import json
import os
import re
import zipfile
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional
import fitz

from backend.config import settings


@dataclass
class DocumentMetadata:
    doc_id: str
    file_name: str
    file_path: str
    file_size_bytes: int
    sha256: str
    page_count: int
    degree: str
    department: str
    department_code: str
    curriculum_version: str
    admission_batch: str
    approval_dates: List[str] = field(default_factory=list)
    has_extractable_text: bool = True
    text_coverage_ratio: float = 1.0
    is_duplicate: bool = False
    duplicate_of: Optional[str] = None
    extraction_status: str = "inventoried"


DEPARTMENT_MAPPING = {
    "civil engineering": ("Civil Engineering", "CE"),
    "data science": ("Computer Science and Engineering (Data Science)", "CSE-DS"),
    "computer science and engineering": ("Computer Science and Engineering", "CSE"),
    "electrical and electronics engineering": ("Electrical and Electronics Engineering", "EEE"),
    "electronics and communication engineering": ("Electronics and Communication Engineering", "ECE"),
    "information technology": ("Information Technology", "IT"),
    "mining engineering": ("Mining Engineering", "MIN"),
    "petroleum technology": ("Petroleum Technology", "PT"),
}


def compute_sha256(file_path: Path) -> str:
    """Compute SHA-256 hash of a file."""
    h = hashlib.sha256()
    with open(file_path, "rb") as f:
        while chunk := f.read(8192 * 16):
            h.update(chunk)
    return h.hexdigest()


def safe_extract_zip(zip_path: Path, target_dir: Path, max_size_bytes: int = 500 * 1024 * 1024) -> List[Path]:
    """Safely extracts zip archive preventing path traversal and zip bombs."""
    target_dir.mkdir(parents=True, exist_ok=True)
    extracted_files = []
    total_size = 0

    with zipfile.ZipFile(zip_path, 'r') as z:
        for member in z.infolist():
            filename = member.filename
            if ".." in filename or filename.startswith("/") or filename.startswith("\\"):
                raise ValueError(f"Malicious archive member detected (path traversal): {filename}")

            total_size += member.file_size
            if total_size > max_size_bytes:
                raise ValueError(f"Archive exceeds maximum allowed size ({max_size_bytes} bytes). Potential zip bomb.")

            target_path = target_dir / filename
            if member.is_dir():
                target_path.mkdir(parents=True, exist_ok=True)
            else:
                target_path.parent.mkdir(parents=True, exist_ok=True)
                with z.open(member) as source, open(target_path, "wb") as target:
                    target.write(source.read())
                extracted_files.append(target_path)

    return extracted_files


def extract_frontmatter_metadata(doc: fitz.Document, filename: str) -> Dict[str, Any]:
    """Extract metadata from title page and front matter."""
    first_pages_text = ""
    for i in range(min(5, len(doc))):
        first_pages_text += f"\n--- Page {i+1} ---\n" + doc[i].get_text()

    fn_lower = filename.lower()
    dept = "General Engineering"
    code = "GEN"

    if "data science" in fn_lower or "cse-ds" in fn_lower:
        dept = "Computer Science and Engineering (Data Science)"
        code = "CSE-DS"
    elif "computer science" in fn_lower or "cse" in fn_lower:
        dept = "Computer Science and Engineering"
        code = "CSE"
    elif "civil" in fn_lower or " ce" in fn_lower:
        dept = "Civil Engineering"
        code = "CE"
    elif "electrical" in fn_lower or "eee" in fn_lower:
        dept = "Electrical and Electronics Engineering"
        code = "EEE"
    elif "electronics" in fn_lower or "ece" in fn_lower:
        dept = "Electronics and Communication Engineering"
        code = "ECE"
    elif "information technology" in fn_lower or " it" in fn_lower:
        dept = "Information Technology"
        code = "IT"
    elif "mining" in fn_lower or "mn. e" in fn_lower:
        dept = "Mining Engineering"
        code = "MIN"
    elif "petroleum" in fn_lower or " pt" in fn_lower:
        dept = "Petroleum Technology"
        code = "PT"

    version_match = re.search(r"Version\s*([0-9\.]+)", first_pages_text, re.IGNORECASE)
    version = f"Version {version_match.group(1)}" if version_match else "Version 3.0"

    batch_match = re.search(r"admitted from A\.?Y\.?\s*([0-9]{4}-[0-9]{2,4})", first_pages_text, re.IGNORECASE)
    batch = batch_match.group(1) if batch_match else "2024-25"

    approval_dates = []
    for line in first_pages_text.splitlines():
        if "Approved in the BoS meeting" in line:
            approval_dates.append(line.strip())

    return {
        "department": dept,
        "department_code": code,
        "degree": "B.Tech.",
        "curriculum_version": version,
        "admission_batch": batch,
        "approval_dates": approval_dates,
    }


class SourceInventoryManager:
    """Discovers, inventories, and validates source documents."""

    def __init__(self, search_dirs: Optional[List[Path]] = None):
        if search_dirs is None:
            if settings.DOCUMENTS_DIR.exists() and any(settings.DOCUMENTS_DIR.glob("*.pdf")):
                search_dirs = [settings.DOCUMENTS_DIR]
            else:
                search_dirs = [settings.BASE_DIR]
        self.search_dirs = search_dirs
        self.manifest_path = settings.MANIFESTS_DIR / "document_manifest.json"
        self.csv_path = settings.MANIFESTS_DIR / "source_inventory.csv"
        self.quality_report_path = settings.MANIFESTS_DIR / "source_quality_report.json"

    def generate_manifest(self) -> Path:
        """Scan documents and return path to generated manifest."""
        self.scan_and_inventory()
        return self.manifest_path

    def scan_and_inventory(self) -> List[DocumentMetadata]:
        """Scan directories, process archives and PDFs, and generate reports."""
        pdf_files: List[Path] = []

        for s_dir in self.search_dirs:
            for z_path in s_dir.glob("*.zip"):
                try:
                    unpacked = safe_extract_zip(z_path, settings.DATA_DIR / "unpacked")
                    pdf_files.extend([p for p in unpacked if p.suffix.lower() == ".pdf"])
                except Exception as e:
                    print(f"Warning extracting {z_path}: {e}")

            for p in s_dir.glob("*.pdf"):
                if p not in pdf_files:
                    pdf_files.append(p)

        pdf_files = sorted(pdf_files, key=lambda x: x.name)
        seen_hashes: Dict[str, str] = {}
        inventory: List[DocumentMetadata] = []

        for idx, pdf_path in enumerate(pdf_files, 1):
            file_size = pdf_path.stat().st_size
            sha256 = compute_sha256(pdf_path)

            doc = fitz.open(pdf_path)
            page_count = len(doc)

            pages_with_text = 0
            sample_size = min(20, page_count)
            for pno in range(sample_size):
                if len(doc[pno].get_text().strip()) > 30:
                    pages_with_text += 1
            text_ratio = round(pages_with_text / max(1, sample_size), 3)
            doc.close()

            doc_reopened = fitz.open(pdf_path)
            meta = extract_frontmatter_metadata(doc_reopened, pdf_path.name)
            doc_reopened.close()

            doc_id = f"DOC-{meta['department_code']}-{idx:02d}"
            is_dup = sha256 in seen_hashes
            dup_of = seen_hashes.get(sha256)
            if not is_dup:
                seen_hashes[sha256] = doc_id

            item = DocumentMetadata(
                doc_id=doc_id,
                file_name=pdf_path.name,
                file_path=str(pdf_path.resolve()),
                file_size_bytes=file_size,
                sha256=sha256,
                page_count=page_count,
                degree=meta["degree"],
                department=meta["department"],
                department_code=meta["department_code"],
                curriculum_version=meta["curriculum_version"],
                admission_batch=meta["admission_batch"],
                approval_dates=meta["approval_dates"],
                has_extractable_text=(text_ratio > 0.5),
                text_coverage_ratio=text_ratio,
                is_duplicate=is_dup,
                duplicate_of=dup_of,
                extraction_status="verified",
            )
            inventory.append(item)

        self._save_artifacts(inventory)
        return inventory

    def _save_artifacts(self, inventory: List[DocumentMetadata]) -> None:
        """Write manifest JSON, inventory CSV, and quality report JSON."""
        settings.MANIFESTS_DIR.mkdir(parents=True, exist_ok=True)

        manifest_data = {
            "institution": settings.INSTITUTION_NAME,
            "location": settings.INSTITUTION_LOCATION,
            "total_documents": len(inventory),
            "total_pages": sum(d.page_count for d in inventory),
            "documents": [asdict(d) for d in inventory],
        }
        with open(self.manifest_path, "w", encoding="utf-8") as f:
            json.dump(manifest_data, f, indent=2)

        with open(self.csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                "doc_id", "department_code", "department", "curriculum_version",
                "admission_batch", "page_count", "file_size_mb", "has_extractable_text",
                "sha256", "file_name"
            ])
            for d in inventory:
                writer.writerow([
                    d.doc_id,
                    d.department_code,
                    d.department,
                    d.curriculum_version,
                    d.admission_batch,
                    d.page_count,
                    round(d.file_size_bytes / (1024 * 1024), 2),
                    d.has_extractable_text,
                    d.sha256,
                    d.file_name,
                ])

        quality_data = {
            "summary": {
                "total_documents": len(inventory),
                "total_pages": sum(d.page_count for d in inventory),
                "valid_documents": sum(1 for d in inventory if d.has_extractable_text and not d.is_duplicate),
                "duplicate_documents": sum(1 for d in inventory if d.is_duplicate),
                "avg_page_count": round(sum(d.page_count for d in inventory) / max(1, len(inventory)), 1),
            },
            "department_coverage": {
                d.department_code: {
                    "department": d.department,
                    "pages": d.page_count,
                    "version": d.curriculum_version,
                    "text_coverage": d.text_coverage_ratio,
                }
                for d in inventory
            },
            "integrity_checks": {
                "all_sha256_unique": len(set(d.sha256 for d in inventory)) == len(inventory),
                "zero_byte_files_found": any(d.file_size_bytes == 0 for d in inventory),
                "all_versions_v3": all("3.0" in d.curriculum_version for d in inventory),
            }
        }
        with open(self.quality_report_path, "w", encoding="utf-8") as f:
            json.dump(quality_data, f, indent=2)


DocumentInventoryManager = SourceInventoryManager
