from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import RouteQuery
from .serializers import NodeSerializer, EdgeSerializer, ShortestRouteRequestSerializer
from .services import find_shortest_route

class NodeListCreateView(APIView):
    def post(self, request):
        serializer = NodeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class EdgeListCreateView(APIView):
    def post(self, request):
        serializer = EdgeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class ShortestRouteView(APIView):
    def post(self, request):
        serializer = ShortestRouteRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        source_node = serializer.validated_data["source"]
        destination_node = serializer.validated_data["destination"]
        result = find_shortest_route(source_node.name, destination_node.name)
        if result is None:
            return Response(
                {"error": f"No path exists between {source_node.name} and {destination_node.name}"},
                status=status.HTTP_404_NOT_FOUND,
            )
        total_latency, path = result
        rounded_latency = round(total_latency, 2)
        # Record successful query in history (D7)
        RouteQuery.objects.create(
            source=source_node.name,
            destination=destination_node.name,
            total_latency=rounded_latency,
            path=path,
        )
        return Response(
            {
                "total_latency": rounded_latency,
                "path": path,
            },
            status=status.HTTP_200_OK,
        )
