from django.shortcuts import render
import calendar
# Create your views here.

from rest_framework.permissions import IsAdminUser, IsAuthenticated
from .serializers import *
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import CreateAPIView, ListAPIView, RetrieveUpdateDestroyAPIView, RetrieveAPIView
from rest_framework.views import APIView
from .models import *
from django.db.models.functions import TruncHour
from django.db.models import Count

from .utils import get_client_ip
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
                'month': calendar.month_abbr[month],
                'rentals': rentals.count()
            })
        return data
    


        
class HourlyUsagePattern(APIView):
    def get(self, request, *args, **kwargs):
        start_of_today = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_today = start_of_today + timedelta(days=1)
        # Aggregate hourly data
        data = (
            UserActivity.objects.filter(timestamp__gte=start_of_today, timestamp__lt=end_of_today)
            .annotate(hour=TruncHour('timestamp'))
            .values('hour')
            .annotate(users=Count('user', distinct=True))
            .order_by('hour')
        )
        # Format data for the chart
        formatted_data = [
            {"hour": item["hour"].strftime("%I %p"), "users": item["users"]}
            for item in data
        ]
        return Response(formatted_data)


# Bike Distribution Statsus
class BikeDistributionStatus(APIView):
    def get(self, request, *args, **kwargs):
        data = {
            'total_bikes': Bike.objects.count(),
            'available_bikes': Bike.objects.filter(status='AVAILABLE').count(),
            'reserved_bikes': Bike.objects.filter(status='RESERVED').count(),
            'under_maintenance': Bike.objects.filter(status='MAINTENANCE').count(),
            'in_use': Bike.objects.filter(status='IN_USE').count(),
        }
        return Response(data)