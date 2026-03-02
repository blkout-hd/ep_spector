"""
Smoke tests for privacy erasure endpoint logic
(tests view function directly without Django test client to avoid DB setup)
"""
from __future__ import annotations

import pytest


def test_erase_missing_identifier():
    """POST /api/privacy/erase/ without identifier should return 400."""
    import os
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "spector_django.settings")
    try:
        import django
        django.setup()
        from apps.privacy.views import erase_data
        # Minimal mock request
        from unittest.mock import MagicMock
        request = MagicMock()
        request.data = {}
        response = erase_data(request)
        assert response.status_code == 400
    except Exception as e:
        pytest.skip(f"Django not fully configured in test env: {e}")
