from django.urls import path
from .views import (
    NodeListCreateView,
    NodeDetailView,
    EdgeListCreateView,
    EdgeDetailView,
    ShortestRouteView,
    RouteHistoryView,
)


urlpatterns = [
    path("nodes", NodeListCreateView.as_view(), name="node-list"),
    path("nodes/<int:pk>", NodeDetailView.as_view(), name="node-detail"),

    path("edges", EdgeListCreateView.as_view(), name="edge-list"),
    path("edges/<int:pk>", EdgeDetailView.as_view(), name="edge-detail"),

    path("routes/shortest", ShortestRouteView.as_view(), name="shortest-route"),
    path("routes/history", RouteHistoryView.as_view(), name="route-history"),
]