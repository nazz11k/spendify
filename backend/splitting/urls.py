from rest_framework.routers import DefaultRouter
from .views import SharedSpentViewSet

router = DefaultRouter()
router.register(r'spents', SharedSpentViewSet, basename='sharedspent')

urlpatterns = router.urls
