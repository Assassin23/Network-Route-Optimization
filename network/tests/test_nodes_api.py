from django.db import IntegrityError
import pytest
from network.models import Edge, RouteQuery, Node

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


@pytest.mark.django_db
def test_list_nodes_returns_all_nodes(api_client):
    Node.objects.create(name="ServerA")
    Node.objects.create(name="ServerB")

    response = api_client.get("/nodes")
    assert response.status_code == 200
    assert len(response.data) == 2
    names = [item["name"] for item in response.data]
    assert "ServerA" in names
    assert "ServerB" in names


@pytest.mark.django_db
def test_delete_node_returns_204(api_client):
    node = Node.objects.create(name="ServerA")
    response = api_client.delete(f"/nodes/{node.id}")

    assert response.status_code == 204
    assert Node.objects.filter(id=node.id).count() == 0


@pytest.mark.django_db
def test_delete_nonexistent_node_returns_404(api_client):
    response = api_client.delete("/nodes/99999")
    assert response.status_code == 404


@pytest.mark.django_db
def test_delete_node_cascades_to_edges_but_preserves_history(api_client):
    node_a = Node.objects.create(name="A")
    node_b = Node.objects.create(name="B")
    edge = Edge.objects.create(source=node_a, destination=node_b, latency=10.0)
    history = RouteQuery.objects.create(
        source="A", destination="B", total_latency=10.0, path=["A", "B"]
    )

    # Deleting node A
    response = api_client.delete(f"/nodes/{node_a.id}")
    assert response.status_code == 204

    # Edge must be cascaded (deleted)
    assert Edge.objects.filter(id=edge.id).count() == 0

    # History must be preserved (D8)
    assert RouteQuery.objects.filter(id=history.id).count() == 1

@pytest.mark.django_db
def test_model_str_methods():
    node_a = Node.objects.create(name="ServerA")
    node_b = Node.objects.create(name="ServerB")
    edge = Edge.objects.create(source=node_a, destination=node_b, latency=12.5)
    query = RouteQuery.objects.create(
        source="ServerA",
        destination="ServerB",
        total_latency=12.5,
        path=["ServerA", "ServerB"],
    )

    assert str(node_a) == "ServerA"
    assert str(edge) == "ServerA -> ServerB (12.5ms)"
    assert str(query) == "ServerA -> ServerB (12.5ms)"
