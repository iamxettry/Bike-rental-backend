from django.shortcuts import render
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from .serializers import BikeSerializer
from .models import Bike
from rest_framework.response import Response
from rest_framework import status

from rest_framework.generics import CreateAPIView, ListAPIView, RetrieveAPIView, UpdateAPIView, DestroyAPIView

# Bike Create API
class BikeCreateView(CreateAPIView):
    serializer_class = BikeSerializer
    permission_classes = [IsAdminUser, IsAuthenticated]
    def post(self, request, *args, **kwargs):
        print("Request Data:", request.data)
        serializer = self.get_serializer(data=request.data)
        
        if serializer.is_valid():
            serializer.save()
            return Response({"success": "Bike Added Successfully."}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Bike Update API

class BikeUpdateView(UpdateAPIView):
    serializer_class = BikeSerializer
    permission_classes = [IsAdminUser, IsAuthenticated]

    def get_queryset(self):
        return Bike.objects.all()


# Bike list view
class BikeListView(ListAPIView):
    serializer_class=BikeSerializer
    pagination_class = None
    def get_queryset(self):
        return Bike.objects.all()

# Bike Retrive view 
class BikeRetriveView(RetrieveAPIView):
    serializer_class = BikeSerializer
    def get(self, request, pk):
        bike = Bike.objects.get(id=pk)
        serializer = self.get_serializer(bike)
        return Response(serializer.data, status=status.HTTP_200_OK)

# Delete Bike 
class BikeDeleteView(DestroyAPIView):
    serializer_class = BikeSerializer
    permission_classes = [IsAdminUser, IsAuthenticated]
    def get_queryset(self):
        return Bike.objects.all()
    
    def delete(self, request, pk):
        bike = Bike.objects.get(id=pk)
        bike.delete()
        return Response({"success": "Bike Deleted Successfully."}, status=status.HTTP_204_NO_CONTENT)

# Featued Bike List View
class FeaturedBikeListView(ListAPIView):
    serializer_class = BikeSerializer
    pagination_class = None
    def get_queryset(self):
        return Bike.objects.filter(isFeatured=True)
    
# Bike Search View
class BikeSearchView(ListAPIView):
    serializer_class = BikeSerializer
    pagination_class = None
    def get_queryset(self):
        query = self.request.GET.get('search')
        return Bike.objects.filter(name__icontains=query)