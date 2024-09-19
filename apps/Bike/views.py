from django.shortcuts import render
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from .serializers import BikeSerializer
from .models import Bike
from rest_framework.response import Response
from rest_framework import status

from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView, CreateAPIView

# Bike Create API
class BikeCreateView(CreateAPIView):
    serializer_class = BikeSerializer
    permission_classes = [IsAdminUser, IsAuthenticated]
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"success": "Bike Added Successfully."}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
