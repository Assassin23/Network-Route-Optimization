from django.urls import path
from .views import NodeListCreateView


urlpatterns = [
    path("nodes", NodeListCreateView.as_view(), name="node-list"),
]