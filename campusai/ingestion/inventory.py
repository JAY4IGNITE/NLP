"""Source inventory module for discovering, validating, and cataloging curriculum documents.
Re-exported from backend.data_ingestion.inventory for backward compatibility.
"""
from backend.data_ingestion.inventory import (
    DocumentMetadata,
    DEPARTMENT_MAPPING,
    compute_sha256,
    safe_extract_zip,
    extract_frontmatter_metadata,
    SourceInventoryManager
)

__all__ = [
    "DocumentMetadata",
    "DEPARTMENT_MAPPING",
    "compute_sha256",
    "safe_extract_zip",
    "extract_frontmatter_metadata",
    "SourceInventoryManager"
]

if __name__ == "__main__":
    mgr = SourceInventoryManager()
    results = mgr.scan_and_inventory()
    print(f"Inventory complete. Processed {len(results)} documents.")
