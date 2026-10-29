"""Ingest and Audit Official Curriculum Handbooks."""
import sys
import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from backend.data_ingestion.inventory import DocumentInventoryManager
from backend.config import settings

def main():
    print("[*] Running Document Ingestion and Inventory Scan...")
    manager = DocumentInventoryManager()
    manifest_path = manager.generate_manifest()
    print(f"[+] Manifest generated at: {manifest_path}")

    # Print summary
    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest = json.load(f)
    print(f"[+] Verified Documents: {manifest.get('document_count', 0)}")
    for doc in manifest.get("documents", []):
        print(f"    - [{doc.get('department_code', 'N/A')}] {doc.get('filename')} ({doc.get('page_count')} pages)")

if __name__ == "__main__":
    main()
