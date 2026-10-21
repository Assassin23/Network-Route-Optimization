import pytest
from network.models import Edge, Node, RouteQuery


@pytest.fixture
def graph_nodes_and_edges():
    """
    Build the sample graph in the database:
    A --12.5--> B --10.9--> D  (total: 23.4)
    A --30.0--> D              (total: 30.0)
    A --5.0---> C --20.0--> D  (total: 25.0)
    E (isolated)
    """
    a = Node.objects.create(name="A")
    b = Node.objects.create(name="B")
    c = Node.objects.create(name="C")
    d = Node.objects.create(name="D")
    e = Node.objects.create(name="E")

    Edge.objects.create(source=a, destination=b, latency=12.5)
    Edge.objects.create(source=b, destination=d, latency=10.9)
    Edge.objects.create(source=a, destination=d, latency=30.0)
    Edge.objects.create(source=a, destination=c, latency=5.0)
    Edge.objects.create(source=c, destination=d, latency=20.0)
    return {"A": a, "B": b, "C": c, "D": d, "E": e}


@pytest.mark.django_db
def test_shortest_route_returns_200_and_path(api_client, graph_nodes_and_edges):
    """
    Test that POST /routes/shortest returns optimal path and total_latency.
    """
    payload = {"source": "A", "destination": "D"}
    response = api_client.post("/routes/shortest", payload, format="json")

    assert response.status_code == 200
    assert response.data["total_latency"] == 23.4
    assert response.data["path"] == ["A", "B", "D"]


@pytest.mark.django_db
def test_shortest_route_no_path_returns_404(api_client, graph_nodes_and_edges):
    """
    Test that POST /routes/shortest returns 404 with error message when no path exists.
    """
    payload = {"source": "A", "destination": "E"}
    response = api_client.post("/routes/shortest", payload, format="json")

    assert response.status_code == 404
    assert response.data == {"error": "No path exists between A and E"}


@pytest.mark.django_db
@pytest.mark.parametrize(
    "payload,missing_key",
    [
        ({"destination": "D"}, "source"),
        ({"source": "A"}, "destination"),
        ({}, "source"),
    ],
)
def test_shortest_route_missing_fields_returns_400(api_client, graph_nodes_and_edges, payload, missing_key):
    response = api_client.post("/routes/shortest", payload, format="json")
    assert response.status_code == 400


@pytest.mark.django_db
def test_shortest_route_unknown_node_returns_400(api_client, graph_nodes_and_edges):
    payload = {"source": "Unknown", "destination": "D"}
    response = api_client.post("/routes/shortest", payload, format="json")
    assert response.status_code == 400

@pytest.mark.django_db
def test_shortest_route_same_node_returns_zero(api_client, graph_nodes_and_edges):
    payload = {"source": "A", "destination": "A"}
    response = api_client.post("/routes/shortest", payload, format="json")

    assert response.status_code == 200
    assert response.data == {"total_latency": 0.0, "path": ["A"]}


@pytest.mark.django_db
def test_successful_query_is_recorded_in_history(api_client, graph_nodes_and_edges):
    payload = {"source": "A", "destination": "D"}
    response = api_client.post("/routes/shortest", payload, format="json")
    assert response.status_code == 200

    assert RouteQuery.objects.count() == 1
    record = RouteQuery.objects.get()
    assert record.source == "A"
    assert record.destination == "D"
    assert record.total_latency == 23.4
    assert record.path == ["A", "B", "D"]


@pytest.mark.django_db
def test_failed_query_is_not_recorded_in_history(api_client, graph_nodes_and_edges):
    # 404 no path
    api_client.post("/routes/shortest", {"source": "A", "destination": "E"}, format="json")
    # 400 unknown node
    api_client.post("/routes/shortest", {"source": "Ghost", "destination": "D"}, format="json")

    assert RouteQuery.objects.count() == 0
