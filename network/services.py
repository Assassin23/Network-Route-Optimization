from collections import defaultdict
import heapq
from typing import Iterable, List, Optional, Tuple
from .models import Edge


def shortest_path(
    edges: Iterable[Tuple[str, str, float]],
    source: str,
    destination: str,
) -> Optional[Tuple[float, List[str]]]:
    """
    Computes the shortest path from source to destination using Dijkstra's algorithm.
    
    Args:
        edges: Iterable of (source_name, destination_name, latency) tuples.
        source: Name of the starting node.
        destination: Name of the target node.
        
    Returns:
        (total_latency, ["ServerA", ...]) or None if no path exists.
    """
    if source == destination:
        return 0.0, [source]

    # Build adjacency list: node -> list of (neighbor, latency)
    graph = defaultdict(list)
    for u, v, latency in edges:
        graph[u].append((v, latency))

    # Priority queue stores tuples of: (current_cost, current_node, path_taken)
    pq = [(0.0, source, [source])]
    min_cost = {source: 0.0}

    while pq:
        current_cost, current_node, path = heapq.heappop(pq)

        if current_node == destination:
            return current_cost, path

        # If we already found a cheaper route to current_node, skip expanding it
        if current_cost > min_cost.get(current_node, float("inf")):
            continue

        for neighbor, latency in graph[current_node]:
            new_cost = current_cost + latency
            if new_cost < min_cost.get(neighbor, float("inf")):
                min_cost[neighbor] = new_cost
                heapq.heappush(pq, (new_cost, neighbor, path + [neighbor]))

    return None


def find_shortest_route(source: str, destination: str) -> Optional[Tuple[float, List[str]]]:
    """
    Fetches all active edges from the database and calculates the shortest route.
    """
    edges = Edge.objects.values_list("source__name", "destination__name", "latency")
    return shortest_path(edges, source, destination)
