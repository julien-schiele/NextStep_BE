from rest_framework.routers import DefaultRouter
from .views import ExerciseViewSet, ProgramViewSet

router = DefaultRouter()
router.register(r"exercises", ExerciseViewSet, basename="exercise")
router.register(r"programs", ProgramViewSet, basename="program")

urlpatterns = router.urls
