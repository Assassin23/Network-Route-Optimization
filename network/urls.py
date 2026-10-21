from django.urls import path
from .views import NodeListCreateView, EdgeListCreateView


urlpatterns = [
    path("nodes", NodeListCreateView.as_view(), name="node-list"),
    path("edges", EdgeListCreateView.as_view(), name="edge-list"),
]