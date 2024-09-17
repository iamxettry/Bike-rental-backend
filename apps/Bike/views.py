from django.shortcuts import render
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from .serializers import BikeSerializer
from .models import Bike

from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView, CreateAPIView

# Bike Create API
class BikeCreateView(CreateAPIView):
    serializer_class = BikeSerializer
    permission_classes = [IsAdminUser, IsAuthenticated]
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)
