from django.db import models


class Node(models.Model):
    """Represent a node in the network with a unique name."""
    name = models.CharField(max_length=100, unique=True)

    def __str__(self) -> str:
        """Return a string representation of the node."""
        return str(self.name)

class Edge(models.Model):
    """Represent a directed weighted edge between two nodes."""
    source = models.ForeignKey(
        Node, on_delete=models.CASCADE, related_name="outgoing_edges"
    )
    destination = models.ForeignKey(
        Node, on_delete=models.CASCADE, related_name="incoming_edges"
    )
    latency = models.FloatField()
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["source", "destination"],
                name="unique_edge_source_destination",
            )
        ]
    def __str__(self):
        return f"{self.source.name} -> {self.destination.name} ({self.latency}ms)"
