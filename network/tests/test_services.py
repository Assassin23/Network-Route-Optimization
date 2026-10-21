import pytest
from network.services import shortest_path


@pytest.fixture
def sample_edges():
    """
    Sample graph:
    A --12.5--> B --10.9--> D (total: 23.4)
    A --30.0--> D             (total: 30.0)
    A --5.0---> C --20.0--> D (total: 25.0)
    E is isolated
    """
    return [
        ("A", "B", 12.5),
        ("B", "D", 10.9),
        ("A", "D", 30.0),
        ("A", "C", 5.0),
        ("C", "D", 20.0),
    ]


def test_shortest_path_direct_edge():
    edges = [("A", "B", 10.0)]
    result = shortest_path(edges, "A", "B")
    assert result == (10.0, ["A", "B"])


def test_shortest_path_picks_cheaper_multi_hop_over_direct(sample_edges):
    # A -> B -> D is 23.4, whereas A -> D is 30.0
    cost, path = shortest_path(sample_edges, "A", "D")
    assert cost == pytest.approx(23.4)
    assert path == ["A", "B", "D"]


def test_shortest_path_unreachable_node_returns_none(sample_edges):
    result = shortest_path(sample_edges, "A", "E")
    assert result is None


def test_shortest_path_respects_edge_direction(sample_edges):
    # D -> A has no path because all edges are directed towards D
    result = shortest_path(sample_edges, "D", "A")
    assert result is None


def test_shortest_path_same_source_and_destination():
    edges = [("A", "B", 10.0)]
    result = shortest_path(edges, "A", "A")
    assert result == (0.0, ["A"])


def test_shortest_path_handles_cycles():
    # Graph has a cycle A <-> B, and B -> C
    edges = [
        ("A", "B", 5.0),
        ("B", "A", 5.0),
        ("B", "C", 10.0),
    ]
    cost, path = shortest_path(edges, "A", "C")
    assert cost == 15.0
    assert path == ["A", "B", "C"]
