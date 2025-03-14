from rest_framework.routers import DefaultRouter
from .viewsets import CommentViewSet, LikeViewSet

router = DefaultRouter()

router.register('comments', CommentViewSet)
router.register('likes', LikeViewSet)

urlpatterns =  router.urls