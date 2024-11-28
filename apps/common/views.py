from django.shortcuts import render

# Create your views here.

from rest_framework.permissions import IsAdminUser, IsAuthenticated
from .serializers import *
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import CreateAPIView, ListAPIView, RetrieveUpdateDestroyAPIView, RetrieveAPIView

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

class LocationRetrive(RetrieveAPIView):
    serializer_class = LocationSerializer

    def get(self, request, pk):
        try:
            bike = Location.objects.get(id=pk)
            serializer = self.get_serializer(bike)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Location.DoesNotExist:
            return Response({"detail": "Location does not exist."}, status=status.HTTP_404_NOT_FOUND)

class LocationRetriveUpdateDestroyView(RetrieveUpdateDestroyAPIView):
    serializer_class = LocationSerializer
    permission_classes = [IsAdminUser, IsAuthenticated]
    def get_queryset(self):
        return Location.objects.all()
    
    # update 
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response({"success": "Location Updated Successfully."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    # delete
    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return Response({"success": "Location Deleted Successfully."}, status=status.HTTP_204_NO_CONTENT)

# location search
class LocationSearchView(ListAPIView):
    serializer_class = LocationSerializer
    pagination_class = None

    def get_queryset(self):
        query = self.request.query_params.get('search')
        return Location.objects.filter(city__icontains=query) if query else Location.objects.all()