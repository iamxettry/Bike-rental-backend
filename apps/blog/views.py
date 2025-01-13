# apps/blog/views.py

from rest_framework import viewsets
from .models import Blog
from .serializers import BlogSerializer
from rest_framework.permissions import IsAuthenticatedOrReadOnly

class BlogViewSet(viewsets.ModelViewSet):
    queryset = Blog.objects.all()
    serializer_class = BlogSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        # Automatically set the author to the currently authenticated user
        serializer.save(author=self.request.user)
