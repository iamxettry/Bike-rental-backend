
from .models import Location
from rest_framework import serializers
from apps.Bike.models import Bike 
from apps.auth.models import User
from apps.Bike_rent.models import BikeRental
from datetime import datetime, timedelta
from django.db.models import Sum
from django.utils import timezone
class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = '__all__'


# Quick stats Serializer 
class QuickStatsSerializer(serializers.Serializer):
    total_bikes = serializers.SerializerMethodField()
    active_rentals = serializers.SerializerMethodField()
    new_users = serializers.SerializerMethodField()
    todays_revenue = serializers.SerializerMethodField()

    def get_total_bikes(self, _):
        return Bike.objects.count()

    def get_active_rentals(self, _):
        return BikeRental.objects.filter(rental_status='active').count()

    def get_new_users(self, _):
        one_month_ago = timezone.now() - timedelta(days=30)
        return User.objects.filter(date_joined__gte=one_month_ago).count()

    def get_todays_revenue(self, _):
        today = timezone.now().date()
        return BikeRental.objects.filter(pickup_date__date=today).aggregate(
            total_revenue=Sum('total_amount')
        )['total_revenue'] or 0
    
    