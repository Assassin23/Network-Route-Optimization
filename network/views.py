from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import NodeSerializer, EdgeSerializer

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
