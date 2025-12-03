from rest_framework.routers import DefaultRouter
from .views import FriendshipViewSet

router = DefaultRouter()
router.register(r'friends', FriendshipViewSet, basename='friendship')

urlpatterns = router.urls
