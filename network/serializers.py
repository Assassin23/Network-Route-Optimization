from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator
from .models import Node, Edge, RouteQuery

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

class ShortestRouteRequestSerializer(serializers.Serializer):
    source = serializers.SlugRelatedField(
        slug_field="name", queryset=Node.objects.all()
    )
    destination = serializers.SlugRelatedField(
        slug_field="name", queryset=Node.objects.all()
    )

class RouteQuerySerializer(serializers.ModelSerializer):
    class Meta:
        model = RouteQuery
        fields = [
            "id",
            "source",
            "destination",
            "total_latency",
            "path",
            "created_at",
        ]
class HistoryFilterSerializer(serializers.Serializer):
    source = serializers.CharField(required=False)
    destination = serializers.CharField(required=False)
    limit = serializers.IntegerField(min_value=1, required=False)
    date_from = serializers.DateTimeField(required=False)
    date_to = serializers.DateTimeField(required=False)
