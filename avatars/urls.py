from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProfileViewSet, SharedImageViewSet

router = DefaultRouter()
router.register(r'profiles', ProfileViewSet, basename='profile')
router.register(r'shared_images', SharedImageViewSet, basename='sharedimage')

urlpatterns = [
    path('', include(router.urls)),
]
