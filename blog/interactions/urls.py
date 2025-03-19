from rest_framework.routers import DefaultRouter
from .viewsets import CommentViewSet, LikeViewSet

router = DefaultRouter()

router.register('comments', CommentViewSet, basename='comments')
router.register('likes', LikeViewSet, basename='likes')

urlpatterns =  router.urls