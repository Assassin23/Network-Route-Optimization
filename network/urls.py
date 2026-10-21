from django.urls import path
from .views import (
    NodeListCreateView, 
    EdgeListCreateView, 
    ShortestRouteView, 
    RouteHistoryView,
)


urlpatterns = [
    path("nodes", NodeListCreateView.as_view(), name="node-list"),
    path("edges", EdgeListCreateView.as_view(), name="edge-list"),
    path("routes/shortest", ShortestRouteView.as_view(), name="shortest-route"),
    path("routes/history", RouteHistoryView.as_view(), name="route-history"),
]