"""
Tests for source inventory management.
"""

from pathlib import Path
from campusai.config import settings
from campusai.ingestion.inventory import SourceInventoryManager, compute_sha256


def test_source_inventory_manager():
    mgr = SourceInventoryManager()
    docs = mgr.scan_and_inventory()
    assert len(docs) == 8
    total_pages = sum(d.page_count for d in docs)
    assert total_pages == 6502

    # Verify artifacts exist
    assert mgr.manifest_path.exists()
    assert mgr.csv_path.exists()
    assert mgr.quality_report_path.exists()

    # Verify CSE doc is present
    cse_doc = next((d for d in docs if d.department_code == "CSE"), None)
    assert cse_doc is not None
    assert cse_doc.curriculum_version == "Version 3.0"
    assert cse_doc.page_count == 808
    assert cse_doc.has_extractable_text is True
