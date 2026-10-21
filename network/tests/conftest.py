import pytest
from rest_framework.test import APIClient


@pytest.fixture
def api_client():
    """Return an unauthenticated DRF APIClient."""
    return APIClient()
