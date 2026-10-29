"""Website connector package for official university web updates."""
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
