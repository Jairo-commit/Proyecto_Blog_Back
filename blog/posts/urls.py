from rest_framework.routers import DefaultRouter
from .viewsets import BlogPostViewSet

router = DefaultRouter()

router.register('post', BlogPostViewSet)

urlpatterns = router.urls