from django.shortcuts import render
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from .serializers import *
from .models import Bike, Rating
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q
from rest_framework.generics import CreateAPIView, ListAPIView, RetrieveAPIView, UpdateAPIView, DestroyAPIView
from rest_framework.views import APIView
from rest_framework.exceptions import ValidationError
# Bike Create API
class BikeCreateView(APIView):
    permission_classes = [IsAdminUser, IsAuthenticated]

    def post(self, request, *args, **kwargs):

        # Handle locations data separately
        locations_data = request.data.getlist("locations[]")
        print("Locations Data 1:", locations_data)

        # Create a new bike instance with the incoming data
        serializer = BikeSerializer(data=request.data)
        
        if serializer.is_valid():
            # First save the bike (without locations)
            bike = serializer.save()

            # Handle locations if provided
            if locations_data:
                try:
                    # Add the locations to the bike
                    for location_uuid in locations_data:
                        location = Location.objects.get(id=location_uuid)
                        bike.locations.add(location)
                except Location.DoesNotExist:
                    return Response({"detail": "One or more locations not found."}, status=status.HTTP_400_BAD_REQUEST)

            # Return the response with the created bike data
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            # Return validation errors if serializer is not valid
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Bike Update API

class BikeUpdateView(APIView):
    permission_classes = [IsAdminUser, IsAuthenticated]

    def get_object(self, bike_id):
        try:
            return Bike.objects.get(id=bike_id)
        except Bike.DoesNotExist:
            raise ValidationError("Bike not found")

    def patch(self, request, *args, **kwargs):
        # Get bike instance by ID from URL parameters
        bike_id = kwargs.get("pk")
        bike = self.get_object(bike_id)

        # Deserialize the incoming request data
        serializer = BikeSerializer(bike, data=request.data, partial=True)
        
        if serializer.is_valid():
            # Handle locations data separately
            locations_data = request.data.getlist("locations[]")
            if locations_data:
                try:
                    bike.locations.clear()
                    for location_uuid in locations_data:
                        location = Location.objects.get(id=location_uuid)
                        bike.locations.add(location)
                except Location.DoesNotExist:
                    return Response({"detail": "One or more locations not found."}, status=status.HTTP_400_BAD_REQUEST)

            serializer.save()

            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class BikeStatusUpdateView(UpdateAPIView):
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
        try:
            bike = Bike.objects.get(id=pk)
            serializer = self.get_serializer(bike)
            print(serializer.data)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Bike.DoesNotExist:
            return Response({"error": "Bike does not exist."}, status=status.HTTP_404_NOT_FOUND)
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
        if query:
            return Bike.objects.filter(
                Q(name__icontains=query) |
                Q(model__icontains=query) |
                Q(brand__icontains=query) 
                # Q(locations__city__icontains=query)
            )
        return Bike.objects.all()
    
# Bike Rating View
class BikeRatingView(CreateAPIView):
    serializer_class = RatingPostSerializer
    permission_classes = [IsAuthenticated]
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response({"success": "Rating Added Successfully."}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


#get bike on locations
class BikeLocationView(ListAPIView):
    serializer_class = BikeSerializer
    pagination_class = None
    def get_queryset(self):
        location_id = self.kwargs.get("pk")
        print("location_id", location_id)
        return Bike.objects.filter(locations=location_id)