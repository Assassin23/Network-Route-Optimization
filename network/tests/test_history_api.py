import pytest
from network.models import Edge, Node, RouteQuery


@pytest.fixture
def sample_history():
    """
    Creates sample history records in chronological order.
    """
    q1 = RouteQuery.objects.create(
        source="A", destination="B", total_latency=10.0, path=["A", "B"]
    )
    q2 = RouteQuery.objects.create(
        source="B", destination="C", total_latency=15.0, path=["B", "C"]
    )
    q3 = RouteQuery.objects.create(
        source="A", destination="C", total_latency=25.0, path=["A", "B", "C"]
    )
    return [q1, q2, q3]


@pytest.mark.django_db
def test_history_returns_200_and_empty_list_initially(api_client):
    response = api_client.get("/routes/history")
    assert response.status_code == 200
    assert response.data == []


@pytest.mark.django_db
def test_history_returns_expected_fields_and_ordering(api_client, sample_history):
    response = api_client.get("/routes/history")
    assert response.status_code == 200
    assert len(response.data) == 3

    # Newest first: q3, then q2, then q1
    assert response.data[0]["id"] == sample_history[2].id
    assert response.data[0]["source"] == "A"
    assert response.data[0]["destination"] == "C"
    assert response.data[0]["total_latency"] == 25.0
    assert response.data[0]["path"] == ["A", "B", "C"]
    assert "created_at" in response.data[0]


@pytest.mark.django_db
def test_history_filter_by_source(api_client, sample_history):
    response = api_client.get("/routes/history?source=B")
    assert response.status_code == 200
    assert len(response.data) == 1
    assert response.data[0]["source"] == "B"
    assert response.data[0]["destination"] == "C"


@pytest.mark.django_db
def test_history_filter_by_destination(api_client, sample_history):
    response = api_client.get("/routes/history?destination=B")
    assert response.status_code == 200
    assert len(response.data) == 1
    assert response.data[0]["destination"] == "B"


@pytest.mark.django_db
def test_history_limit(api_client, sample_history):
    response = api_client.get("/routes/history?limit=2")
    assert response.status_code == 200
    assert len(response.data) == 2
    # Should return 2 newest
    assert response.data[0]["id"] == sample_history[2].id
    assert response.data[1]["id"] == sample_history[1].id


@pytest.mark.django_db
@pytest.mark.parametrize("invalid_limit", [0, -1, "abc"])
def test_history_invalid_limit_returns_400(api_client, invalid_limit):
    response = api_client.get(f"/routes/history?limit={invalid_limit}")
    assert response.status_code == 400


@pytest.mark.django_db
def test_history_filter_by_date_range(api_client):
    from datetime import timedelta
    from django.utils import timezone

    now = timezone.now()

    # Create queries at different times
    q_past = RouteQuery.objects.create(
        source="A", destination="B", total_latency=10.0, path=["A", "B"]
    )
    RouteQuery.objects.filter(id=q_past.id).update(created_at=now - timedelta(days=2))

    q_target = RouteQuery.objects.create(
        source="B", destination="C", total_latency=15.0, path=["B", "C"]
    )
    RouteQuery.objects.filter(id=q_target.id).update(created_at=now - timedelta(days=1))

    q_future = RouteQuery.objects.create(
        source="A", destination="C", total_latency=25.0, path=["A", "B", "C"]
    )
    RouteQuery.objects.filter(id=q_future.id).update(created_at=now)

    # Format with 'Z' suffix (ISO 8601 UTC) to avoid unescaped '+' in query params
    date_from = (now - timedelta(days=1, hours=2)).strftime("%Y-%m-%dT%H:%M:%SZ")
    date_to = (now - timedelta(hours=12)).strftime("%Y-%m-%dT%H:%M:%SZ")

    response = api_client.get(f"/routes/history?date_from={date_from}&date_to={date_to}")
    assert response.status_code == 200
    assert len(response.data) == 1
    assert response.data[0]["id"] == q_target.id


@pytest.mark.django_db
def test_shortest_route_then_history_shows_it(api_client):
    """
    End-to-end test: calculate shortest route, then fetch history to verify it is listed.
    """
    node_a = Node.objects.create(name="A")
    node_b = Node.objects.create(name="B")
    Edge.objects.create(source=node_a, destination=node_b, latency=14.2)

    # 1. Query shortest route
    res_route = api_client.post(
        "/routes/shortest", {"source": "A", "destination": "B"}, format="json"
    )
    assert res_route.status_code == 200

    # 2. Fetch history
    res_hist = api_client.get("/routes/history")
    assert res_hist.status_code == 200
    assert len(res_hist.data) == 1
    assert res_hist.data[0]["source"] == "A"
    assert res_hist.data[0]["destination"] == "B"
    assert res_hist.data[0]["total_latency"] == 14.2
    assert res_hist.data[0]["path"] == ["A", "B"]
