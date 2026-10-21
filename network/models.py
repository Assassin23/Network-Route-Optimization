from django.db import models


class Node(models.Model):
    """Represent a node in the network with a unique name."""
    name = models.CharField(max_length=100)

    def __str__(self):
        """Return a string representation of the node."""
        return self.name
