from django.shortcuts import render

# Create your views here.

from rest_framework.permissions import IsAdminUser, IsAuthenticated
from .serializers import *
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import CreateAPIView, ListAPIView, RetrieveUpdateDestroyAPIView, RetrieveAPIView
from rest_framework.views import APIView
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

# Quick Stat View 

class QuickStatsViews(APIView):

    permission_classes = [IsAdminUser, IsAuthenticated]
    def get(self, request, *args, **kwargs):
        data = {
            'total_bikes': Bike.objects.count(),
            'active_rentals': BikeRental.objects.filter(rental_status='active').count(),
            'new_users': self.get_new_users(),
            'todays_revenue': self.get_todays_revenue(),
        }
        return Response(data)

    def get_new_users(self):
        one_month_ago = timezone.now() - timedelta(days=30)
        return User.objects.filter(date_joined__gte=one_month_ago).count()

    def get_todays_revenue(self):
        today = timezone.now().date()
        return BikeRental.objects.filter(pickup_date__date=today).aggregate(
            total_revenue=Sum('total_amount')
        )['total_revenue'] or 0


# Get monthly rental count
class MonthlyRentalCount(APIView):
    permission_classes = [IsAdminUser, IsAuthenticated]

    def get(self, request, *args, **kwargs):
        data = self.get_monthly_rental_count()
        return Response(data)

    def get_monthly_rental_count(self):
        # Get year wise rental count
        year = self.request.query_params.get('year', timezone.now().year)

        data = []
        for month in range(1, 13):
            rentals = BikeRental.objects.filter(pickup_date__month=month, pickup_date__year=year) 
            data.append({
                'month': month,
                'count': rentals.count()
            })
        return data