"""
Unit tests for configuration and settings.
"""

from campusai.config import settings


def test_settings_loaded():
    assert settings.APP_NAME == "CampusAI"
    assert "Aditya University" in settings.INSTITUTION_NAME
    assert settings.BASE_DIR.exists()
    assert settings.DATA_DIR.exists()
    assert settings.PROCESSED_DIR.exists()
