from django.urls import path
from .views import nodes_by_owner

urlpatterns = [
    path("by-owner/<int:owner_id>/", nodes_by_owner),
]
