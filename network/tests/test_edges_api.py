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
