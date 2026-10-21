from django.db import IntegrityError
import pytest
from rest_framework.test import APIClient
from network.models import Node

@pytest.mark.django_db
def test_create_node_returns_201(api_client):
    """
    Test that POST /nodes returns 201 Created for valid node data.
    """
    response = api_client.post("/nodes", {"name": "ServerA"}, format="json")
    assert response.status_code == 201

@pytest.mark.django_db
def test_create_node_returns_id_and_name(api_client):
    """
    Test that POST /nodes returns the created node's id and name.
    """
    response = api_client.post("/nodes", {"name": "ServerA"}, format="json")
    assert response.data["name"] == "ServerA"
    assert isinstance(response.data["id"], int)

@pytest.mark.django_db
def test_create_node_persists_to_db(api_client):
    """
    Test that POST /nodes saves the node in the database.
    """
    response = api_client.post("/nodes", {"name": "ServerA"}, format="json")

    assert Node.objects.count() == 1
    node = Node.objects.get()
    assert node.name == "ServerA"
    assert node.id == response.data["id"]

@pytest.mark.django_db
@pytest.mark.parametrize(
    "payload",
    [{}, {"name": ""}, {"name": "   "}, {"name": None}],
    ids=["missing", "blank", "whitespace", "null"],
)
def test_create_node_with_invalid_name_returns_400(api_client, payload):
    """
    Test that POST /nodes rejects a missing, blank, whitespace-only or null name.
    """
    response = api_client.post("/nodes", payload, format="json")

    assert response.status_code == 400
    assert "name" in response.data
    assert Node.objects.count() == 0

@pytest.mark.django_db
def test_duplicate_node_name_returns_400(api_client):
    """
    Test that POST /nodes rejects duplicate node names with 400 Bad Request.
    """
    # First creation succeeds
    res1 = api_client.post("/nodes", {"name": "ServerA"}, format="json")
    assert res1.status_code == 201

    # Second creation with the same name fails
    res2 = api_client.post("/nodes", {"name": "ServerA"}, format="json")
    assert res2.status_code == 400
    assert "name" in res2.data
    assert Node.objects.count() == 1

@pytest.mark.django_db
def test_node_name_is_unique_in_db():
    """
    Test that the database enforces uniqueness on Node.name directly.
    """
    Node.objects.create(name="ServerA")
    with pytest.raises(IntegrityError):
        Node.objects.create(name="ServerA")
