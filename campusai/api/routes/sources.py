"""
Secure PDF source viewer and page rendering endpoint.
Protects against path traversal and serves page metadata and page images.
"""

from pathlib import Path
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Response
from fastapi.responses import FileResponse
import fitz
from sqlalchemy.orm import Session
from campusai.api.dependencies import get_db
from campusai.config import settings
from campusai.database.models import SourceDocument

router = APIRouter(prefix="/sources", tags=["Source Evidence Viewer"])


@router.get("/{doc_id}")
def get_source_details(doc_id: str, db: Session = Depends(get_db)):
    """Retrieve metadata and page count for a verified source document."""
    doc = db.query(SourceDocument).filter(SourceDocument.doc_id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Source document not found")

    return {
        "doc_id": doc.doc_id,
        "file_name": doc.file_name,
        "department_code": doc.department_code,
        "curriculum_version": doc.curriculum_version,
        "total_pages": doc.total_pages,
        "sha256": doc.sha256,
        "status": doc.extraction_status
    }


@router.get("/{doc_id}/page/{page_number}")
def render_source_page(
    doc_id: str,
    page_number: int,
    format: str = Query("image", description="'image' for PNG or 'text' for raw text"),
    db: Session = Depends(get_db)
):
    """Securely render a specific page of a curriculum PDF.

    Validates document identifier against database to prevent arbitrary file access.
    """
    doc_record = db.query(SourceDocument).filter(SourceDocument.doc_id == doc_id).first()
    if not doc_record:
        raise HTTPException(status_code=404, detail="Source document not found")

    # Locate actual PDF in workspace
    pdf_path = settings.DOCUMENTS_DIR / doc_record.file_name
    if not pdf_path.exists():
        pdf_path = settings.BASE_DIR / doc_record.file_name
    if not pdf_path.exists():
        # Check in unpacked if applicable
        pdf_path = settings.DATA_DIR / "unpacked" / doc_record.file_name

    if not pdf_path.exists():
        raise HTTPException(status_code=404, detail="Underlying document file not found on disk")

    try:
        doc = fitz.open(pdf_path)
        if page_number < 1 or page_number > len(doc):
            doc.close()
            raise HTTPException(status_code=400, detail=f"Page number out of bounds (1-{len(doc)})")

        page = doc[page_number - 1]

        if format == "text":
            text = page.get_text()
            doc.close()
            return {
                "doc_id": doc_id,
                "page_number": page_number,
                "text": text
            }

        # Render page as PNG image at 150 DPI for crystal clear web display
        pix = page.get_pixmap(dpi=150)
        img_bytes = pix.tobytes("png")
        doc.close()

        return Response(content=img_bytes, media_type="image/png")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to render source page: {str(e)}")
