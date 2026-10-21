from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator
from .models import Node, Edge

class NodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Node
        fields = ["id", "name"]

class EdgeSerializer(serializers.ModelSerializer):
    source = serializers.SlugRelatedField(
        slug_field="name", queryset=Node.objects.all()
    )
    destination = serializers.SlugRelatedField(
        slug_field="name", queryset=Node.objects.all()
    )
    class Meta:
        model = Edge
        fields = ["id", "source", "destination", "latency"]
        validators = [
            UniqueTogetherValidator(
                queryset=Edge.objects.all(),
                fields=["source", "destination"],
                message="An edge between these nodes already exists.",
            )
        ]
    def validate_latency(self, value):
        if value <= 0:
            raise serializers.ValidationError("Latency must be a positive number greater than 0.")
        return value
    def validate(self, attrs):
        source = attrs.get("source")
        destination = attrs.get("destination")
        if source and destination and source == destination:
            raise serializers.ValidationError("Self-loops are not allowed: source and destination cannot be identical.")
        return attrs


