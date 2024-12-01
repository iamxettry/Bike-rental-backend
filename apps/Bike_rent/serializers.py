from rest_framework import serializers
from .models import BikeRental
from django.utils import timezone
from apps.Bike.serializers import BikeSerializer

class BikeRentalSerializer(serializers.ModelSerializer):
    bike_details = BikeSerializer(source='bike', read_only=True)
    
    class Meta:
        model = BikeRental
        fields = [
            'id', 'bike', 'bike_details', 'pickup_location', 'dropoff_location',
            'pickup_date', 'dropoff_date', 'payment_status', 'rental_status',
            'total_amount', 'created_at'
        ]
        read_only_fields = ['user', 'payment_status', 'rental_status', 'total_amount']

    def validate(self, data):
        # Validate pickup and dropoff dates
        if data['dropoff_date'] <= data['pickup_date']:
            raise serializers.ValidationError("Dropoff date must be after pickup date")
        
        if data['pickup_date'] < timezone.now():
            raise serializers.ValidationError("Pickup date cannot be in the past")
        
        # Validate bike availability
        bike = data['bike']
        if bike.isAvailable == False:
            raise serializers.ValidationError(f"Bike {bike.name} is not available for rent")
        
        return data
