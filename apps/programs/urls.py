from rest_framework.routers import DefaultRouter
from .views import ExerciseFiltersView, ExerciseViewSet, ProgramFiltersView, ProgramViewSet
from django.urls import path

router = DefaultRouter()

router.register(r"exercises", ExerciseViewSet, basename="exercise")
router.register(r"programs", ProgramViewSet, basename="program")

urlpatterns = [
    path("exercises/filters/", ExerciseFiltersView.as_view(), name="exercise-filters"),
    path("programs/filters/", ProgramFiltersView.as_view(), name="program-filters"),
]

urlpatterns += router.urls
