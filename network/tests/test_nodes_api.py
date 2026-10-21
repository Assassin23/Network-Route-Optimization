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

@pytest.mark.django_db
def test_create_node_returns_id_and_name():
    """
    Test that POST /nodes returns the created node's id and name.
    """
    client = APIClient()
    response = client.post("/nodes", {"name": "ServerA"}, format="json")
    assert response.data["name"] == "ServerA"
    assert isinstance(response.data["id"], int)