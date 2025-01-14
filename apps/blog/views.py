# apps/blog/views.py

from rest_framework import viewsets
from .models import Blog
from .serializers import BlogSerializer
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status
from apps.auth.models import User
from apps.auth.serializers import UserSerializer
class BlogViewSet(viewsets.ModelViewSet):
    queryset = Blog.objects.all()
    serializer_class = BlogSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        print("User:", self.request.user, "Authenticated:", self.request.user.is_authenticated)
        # Automatically set the author to the currently authenticated user
        serializer.save(author=self.request.user)

    def get_queryset(self):
        # Filter by status or return all by default
        queryset = super().get_queryset()
        search = self.request.query_params.get('search', None)
     
        if search:
            queryset= queryset.filter(title=search) | queryset.filter(description__icontains=search)
        return queryset
# get author details 
class AutherRetrive(generics.RetrieveAPIView):
    serializer_class = UserSerializer
    def get(self, request, pk):
        user = User.objects.get(id=pk)
        serializer = self.get_serializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)