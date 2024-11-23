from django.shortcuts import render

# Create your views here.

from rest_framework.permissions import IsAdminUser, IsAuthenticated
from .serializers import *
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import CreateAPIView, ListAPIView, RetrieveUpdateDestroyAPIView

# Create Location API
class LocationCreateView(CreateAPIView):
    serializer_class = LocationSerializer
    permission_classes = [IsAdminUser, IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response({"success": "Location Added Successfully."}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

# List, update, deltete location

class LocationListView(ListAPIView):
    serializer_class = LocationSerializer
    pagination_class = None

    def get_queryset(self):
        return Location.objects.all()

class LocationRetriveUpdateDestroyView(RetrieveUpdateDestroyAPIView):
    serializer_class = LocationSerializer
    permission_classes = [IsAdminUser, IsAuthenticated]
    def get_queryset(self):
        return Location.objects.all()
