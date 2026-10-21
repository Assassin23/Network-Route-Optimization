import pytest
from rest_framework.test import APIClient

@pytest.mark.django_db
def test_create_node_returns_201():
    """
    Test that POST /nodes returns 201 Created for valid node data.
    """
    client = APIClient()
    response = client.post("/nodes", {"name": "ServerA"}, format="json")
    assert response.status_code == 201