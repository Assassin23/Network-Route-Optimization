import pytest
from network.models import Node, Edge


@pytest.mark.django_db
def test_create_edge_returns_201(api_client):
    """
    Test that POST /edges returns 201 Created when creating a valid edge.
    """
    Node.objects.create(name="ServerA")
    Node.objects.create(name="ServerB")

    payload = {
        "source": "ServerA",
        "destination": "ServerB",
        "latency": 12.5,
    }
    response = api_client.post("/edges", payload, format="json")

    assert response.status_code == 201

@pytest.mark.django_db
def test_create_edge_returns_expected_fields(api_client):
    """
    Test that POST /edges returns id, source name, destination name, and latency.
    """
    Node.objects.create(name="ServerA")
    Node.objects.create(name="ServerB")
    payload = {
        "source": "ServerA",
        "destination": "ServerB",
        "latency": 12.5,
    }
    response = api_client.post("/edges", payload, format="json")
    assert isinstance(response.data["id"], int)
    assert response.data["source"] == "ServerA"
    assert response.data["destination"] == "ServerB"
    assert response.data["latency"] == 12.5

@pytest.mark.django_db
def test_create_edge_persists_to_db(api_client):
    """
    Test that POST /edges properly persists the edge in the database.
    """
    node_a = Node.objects.create(name="ServerA")
    node_b = Node.objects.create(name="ServerB")
    payload = {
        "source": "ServerA",
        "destination": "ServerB",
        "latency": 12.5,
    }
    response = api_client.post("/edges", payload, format="json")
    assert Edge.objects.count() == 1
    edge = Edge.objects.get()
    assert edge.source == node_a
    assert edge.destination == node_b
    assert edge.latency == 12.5
    assert edge.id == response.data["id"]

@pytest.mark.django_db
@pytest.mark.parametrize(
    "payload,missing_field",
    [
        ({"destination": "ServerB", "latency": 10.0}, "source"),
        ({"source": "ServerA", "latency": 10.0}, "destination"),
        ({"source": "ServerA", "destination": "ServerB"}, "latency"),
    ],
)
def test_create_edge_missing_fields_returns_400(api_client, payload, missing_field):
    """
    Test that POST /edges returns 400 if any required field is missing.
    """
    Node.objects.create(name="ServerA")
    Node.objects.create(name="ServerB")

    response = api_client.post("/edges", payload, format="json")

    assert response.status_code == 400
    assert missing_field in response.data
    assert Edge.objects.count() == 0


@pytest.mark.django_db
@pytest.mark.parametrize(
    "payload,error_field",
    [
        ({"source": "Unknown", "destination": "ServerB", "latency": 10.0}, "source"),
        ({"source": "ServerA", "destination": "Unknown", "latency": 10.0}, "destination"),
    ],
)
def test_create_edge_unknown_node_returns_400(api_client, payload, error_field):
    """
    Test that POST /edges returns 400 if either source or destination does not exist.
    """
    Node.objects.create(name="ServerA")
    Node.objects.create(name="ServerB")

    response = api_client.post("/edges", payload, format="json")

    assert response.status_code == 400
    assert error_field in response.data
    assert Edge.objects.count() == 0


@pytest.mark.django_db
@pytest.mark.parametrize("latency", [0, -1, -0.01, "fast"])
def test_create_edge_with_invalid_latency_returns_400(api_client, latency):
    """
    Test that POST /edges rejects non-positive or non-numeric latency with 400.
    """
    Node.objects.create(name="ServerA")
    Node.objects.create(name="ServerB")

    payload = {
        "source": "ServerA",
        "destination": "ServerB",
        "latency": latency,
    }
    response = api_client.post("/edges", payload, format="json")

    assert response.status_code == 400
    assert "latency" in response.data
    assert Edge.objects.count() == 0


@pytest.mark.django_db
def test_create_edge_self_loop_returns_400(api_client):
    """
    Test that POST /edges rejects self-loops (source == destination) with 400.
    """
    Node.objects.create(name="ServerA")

    payload = {
        "source": "ServerA",
        "destination": "ServerA",
        "latency": 5.0,
    }
    response = api_client.post("/edges", payload, format="json")

    assert response.status_code == 400
    assert Edge.objects.count() == 0


@pytest.mark.django_db
def test_duplicate_edge_returns_400(api_client):
    """
    Test that duplicate edges between the same source and destination return 400.
    """
    Node.objects.create(name="ServerA")
    Node.objects.create(name="ServerB")

    payload = {
        "source": "ServerA",
        "destination": "ServerB",
        "latency": 10.0,
    }
    res1 = api_client.post("/edges", payload, format="json")
    assert res1.status_code == 201

    res2 = api_client.post("/edges", payload, format="json")
    assert res2.status_code == 400
    assert Edge.objects.count() == 1


@pytest.mark.django_db
def test_reverse_edge_is_allowed(api_client):
    """
    Test that reverse edge (B -> A) is allowed even if (A -> B) exists.
    """
    Node.objects.create(name="ServerA")
    Node.objects.create(name="ServerB")

    res1 = api_client.post(
        "/edges",
        {"source": "ServerA", "destination": "ServerB", "latency": 10.0},
        format="json",
    )
    assert res1.status_code == 201

    res2 = api_client.post(
        "/edges",
        {"source": "ServerB", "destination": "ServerA", "latency": 15.0},
        format="json",
    )
    assert res2.status_code == 201
    assert Edge.objects.count() == 2

@pytest.mark.django_db
def test_list_edges_returns_all_edges_with_names(api_client):
    node_a = Node.objects.create(name="ServerA")
    node_b = Node.objects.create(name="ServerB")
    Edge.objects.create(source=node_a, destination=node_b, latency=10.0)

    response = api_client.get("/edges")
    assert response.status_code == 200
    assert len(response.data) == 1
    assert response.data[0]["source"] == "ServerA"
    assert response.data[0]["destination"] == "ServerB"
    assert response.data[0]["latency"] == 10.0


@pytest.mark.django_db
def test_delete_edge_returns_204(api_client):
    node_a = Node.objects.create(name="ServerA")
    node_b = Node.objects.create(name="ServerB")
    edge = Edge.objects.create(source=node_a, destination=node_b, latency=10.0)

    response = api_client.delete(f"/edges/{edge.id}")
    assert response.status_code == 204
    assert Edge.objects.filter(id=edge.id).count() == 0


@pytest.mark.django_db
def test_delete_nonexistent_edge_returns_404(api_client):
    response = api_client.delete("/edges/99999")
    assert response.status_code == 404


@pytest.mark.django_db
def test_route_changes_after_edge_deleted(api_client):
    """
    Test that deleting an edge causes subsequent route calculation to choose alternate path.
    """
    node_a = Node.objects.create(name="A")
    node_b = Node.objects.create(name="B")
    node_c = Node.objects.create(name="C")

    # Direct edge A -> C is 30ms
    Edge.objects.create(source=node_a, destination=node_c, latency=30.0)
    # Cheaper multi-hop A -> B -> C is 15ms
    Edge.objects.create(source=node_a, destination=node_b, latency=5.0)
    cheap_edge = Edge.objects.create(source=node_b, destination=node_c, latency=10.0)

    # Initially takes cheaper path A -> B -> C (15.0)
    res1 = api_client.post("/routes/shortest", {"source": "A", "destination": "C"}, format="json")
    assert res1.data["total_latency"] == 15.0
    assert res1.data["path"] == ["A", "B", "C"]

    # Delete the cheap edge B -> C
    del_res = api_client.delete(f"/edges/{cheap_edge.id}")
    assert del_res.status_code == 204

    # Subsequent query now falls back to direct A -> C (30.0)
    res2 = api_client.post("/routes/shortest", {"source": "A", "destination": "C"}, format="json")
    assert res2.data["total_latency"] == 30.0
    assert res2.data["path"] == ["A", "C"]
