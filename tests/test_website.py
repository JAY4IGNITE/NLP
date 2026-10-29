import pytest
from campusai.website.connector import AdityaWebsiteConnector, SourceCategory, SimpleHTMLTextExtractor

def test_html_text_extractor():
    html = """
    <html>
        <head><title>Academic Notices - Aditya</title></head>
        <body>
            <h1>Notice 1</h1>
            <p>Registration deadline is <b>Nov 10</b>.</p>
            <script>console.log("bad");</script>
        </body>
    </html>
    """
    parser = SimpleHTMLTextExtractor()
    parser.feed(html)
    assert "Academic Notices - Aditya" in parser.title
    text = parser.get_text()
    assert "Notice 1" in text
    assert "Registration deadline is Nov 10." in text
    assert "console.log" not in text

def test_website_connector_allowlist_and_robots():
    connector = AdityaWebsiteConnector()
    assert connector.is_url_allowed("https://www.adityauniversity.in/academic-calendar") is True
    assert connector.is_url_allowed("/examination-notifications") is True
    assert connector.is_url_allowed("https://malicious-site.com/fake") is False

    assert connector.check_robots_txt("/academic-calendar") is True
    assert connector.check_robots_txt("/portal/student/grades") is False
    assert connector.check_robots_txt("/admin/login") is False

def test_website_connector_ingestion(tmp_path):
    connector = AdityaWebsiteConnector(cache_dir=tmp_path)
    docs = connector.ingest_all_verified_endpoints()
    assert len(docs) >= 3
    calendar_doc = next(d for d in docs if d.category == SourceCategory.ACADEMIC_CALENDAR)
    assert "Academic Calendar" in calendar_doc.title
    assert "Mid-Term Examinations" in calendar_doc.content_text
    assert calendar_doc.is_stale is False
