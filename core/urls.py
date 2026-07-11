from django.urls import path, include
from rest_framework.routers import DefaultRouter
from core.views import TaskViewSet, ProjectViewSet

router = DefaultRouter()
router.register(r"tasks", TaskViewSet, basename="task")
router.register(r"projects", ProjectViewSet, basename="project")

urlpatterns = [
    path("api/", include(router.urls)),
]
