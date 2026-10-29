"""Official Aditya University Website Connector. Re-exported from backend.website.connector."""
from backend.website.connector import (
    SourceCategory,
    WebsiteDocument,
    SimpleHTMLTextExtractor,
    AdityaWebsiteConnector
)

__all__ = [
    "SourceCategory",
    "WebsiteDocument",
    "SimpleHTMLTextExtractor",
    "AdityaWebsiteConnector"
]

if __name__ == "__main__":
    connector = AdityaWebsiteConnector()
    docs = connector.ingest_all_verified_endpoints()
    print(f"Successfully ingested {len(docs)} official Aditya University web resources:")
    for d in docs:
        print(f" - [{d.category.value}] {d.title} ({len(d.content_text)} chars, hash: {d.checksum[:8]})")
