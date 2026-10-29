"""
Command-Line Interface (CLI) for CampusAI.
Provides subcommands:
  - inventory: Discover and validate curriculum source documents.
  - extract: Ingest and parse PDF curriculum tables and units.
  - seed-db: Populate the database with extracted academic records.
  - index: Build BM25 and dense vector search indices.
  - train-intent: Train and evaluate intent recognition models.
  - evaluate: Run full system benchmark suite.
  - serve: Start the FastAPI backend server.
"""

import sys
import argparse
from campusai.ingestion.inventory import SourceInventoryManager


def run_inventory():
    print("=" * 60)
    print(" CampusAI Source Inventory Manager - Aditya University")
    print("=" * 60)
    mgr = SourceInventoryManager()
    docs = mgr.scan_and_inventory()
    print(f"\n[OK] Successfully discovered and inventoried {len(docs)} documents.")
    total_pages = sum(d.page_count for d in docs)
    print(f"Total Academic Pages: {total_pages:,}")
    print("\nDocuments cataloged:")
    for d in docs:
        size_mb = d.file_size_bytes / (1024 * 1024)
        print(f" - [{d.doc_id}] {d.department} ({d.department_code}): {d.page_count} pages ({size_mb:.1f} MB) - {d.curriculum_version}")
    print("\nArtifacts saved:")
    print(f" - Manifest: {mgr.manifest_path}")
    print(f" - Inventory CSV: {mgr.csv_path}")
    print(f" - Quality Report: {mgr.quality_report_path}")
    return docs


def main():
    parser = argparse.ArgumentParser(
        prog="campusai",
        description="CampusAI Autonomous Academic Helpdesk CLI"
    )
    subparsers = parser.add_subparsers(dest="command", help="Available subcommands")

    # inventory
    subparsers.add_parser("inventory", help="Run automated source document inventory")

    # extract
    extract_p = subparsers.add_parser("extract", help="Extract curriculum records from inventoried PDFs")
    extract_p.add_argument("--limit-pages", type=int, default=None, help="Optional max pages per PDF")

    # seed-db
    subparsers.add_parser("seed-db", help="Seed academic database with extracted records")

    # index
    subparsers.add_parser("index", help="Build BM25 and dense embedding indices")

    # train-intent
    subparsers.add_parser("train-intent", help="Train and benchmark intent classification models")

    # evaluate
    subparsers.add_parser("evaluate", help="Run comprehensive evaluation benchmarks")

    # serve
    serve_p = subparsers.add_parser("serve", help="Start the FastAPI backend server")
    serve_p.add_argument("--host", default="0.0.0.0", help="Host address")
    serve_p.add_argument("--port", type=int, default=8000, help="Port")
    serve_p.add_argument("--reload", action="store_true", help="Enable live reload")

    args = parser.parse_args()

    if args.command == "inventory":
        run_inventory()
    elif args.command == "serve":
        import uvicorn
        uvicorn.run("campusai.api.main:app", host=args.host, port=args.port, reload=args.reload)
    elif args.command is None:
        parser.print_help()
    else:
        print(f"Subcommand '{args.command}' will be executed through its dedicated module.")


if __name__ == "__main__":
    main()
