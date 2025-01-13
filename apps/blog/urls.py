# apps/blog/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BlogViewSet,AutherRetrive

router = DefaultRouter()
router.register(r'blogs', BlogViewSet, basename='blog')


urlpatterns = [
    path('', include(router.urls)),
    path('author/<uuid:pk>/', AutherRetrive.as_view(), name='author-blog'),

]
