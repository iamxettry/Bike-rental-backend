from rest_framework import serializers, exceptions
from .models import BikeRental
from django.utils import timezone
from datetime import datetime
from apps.Bike.serializers import BikeSerializer
from apps.auth.serializers import UserSerializer
from apps.common.serializers import LocationSerializer

class BikeRentalSerializer(serializers.ModelSerializer):
    bike_details = BikeSerializer(source='bike', read_only=True)
    user_details = UserSerializer(source='user', read_only=True)
    pickupLocation = serializers.CharField(source="pickup_location", read_only=True)
    dropoffLocation = serializers.CharField(source="dropoff_location", read_only=True)
    pickup_date = serializers.DateTimeField(format="%Y-%m-%dT%H:%M:%S")
    dropoff_date = serializers.DateTimeField(format="%Y-%m-%dT%H:%M:%S")
    class Meta:
        model = BikeRental
        fields = [
            'id', 'bike', 'user_details', 'bike_details', 'pickupLocation', 'dropoffLocation',
            'pickup_date', 'dropoff_date', 'payment_status', 'rental_status','payment_method',
            'total_amount', 'created_at'
        ]
        read_only_fields = ['user', 'total_amount']

    def validate(self, data):
        try:
            instance = self.instance
            # Ensure dates are datetime objects
            pickup_date = data.get('pickup_date', getattr(instance, 'pickup_date', None))
            dropoff_date = data.get('dropoff_date', getattr(instance, 'dropoff_date', None))
            
            if pickup_date and dropoff_date:
                if not isinstance(pickup_date, datetime):
                    pickup_date = timezone.make_aware(datetime.strptime(pickup_date, "%Y-%m-%dT%H:%M:%S"))
                if not isinstance(dropoff_date, datetime):
                    dropoff_date = timezone.make_aware(datetime.strptime(dropoff_date, "%Y-%m-%dT%H:%M:%S"))
            
                data['pickup_date'] = pickup_date
                data['dropoff_date'] = dropoff_date

                # Validate dropoff_date is after pickup_date
                if dropoff_date <= pickup_date:
                    raise exceptions.APIException("Dropoff date must be after pickup date.")

                # Validation for past dates only during creation
                if not instance:  # Only check past dates when creating a new rental
                    if pickup_date.date() < timezone.now().date():
                        raise exceptions.APIException("Pickup date cannot be in the past.")
                    elif pickup_date < timezone.now():
                        raise exceptions.APIException("Pickup time must be later than the current time.")
            
            # Validate bike availability during creation
            if not self.instance and 'bike' in data:
                bike = data['bike']
                if bike.status not in ['AVAILABLE', 'RESERVED']:
                    raise exceptions.APIException(f"Bike {bike.name} is not available for rent.")
            
            return data
        except ValueError as e:
            raise exceptions.APIException(f"Invalid date format. Please use YYYY-MM-DDTHH:MM:SS format. Error: {str(e)}")
    def calculate_total_amount(self, bike, pickup_date, dropoff_date):
        """Calculate the total rental amount based on duration and bike rate"""
        duration = dropoff_date - pickup_date
        days = duration.days  # Get only the days component
        if duration.seconds > 0:  # If there are any hours/minutes/seconds, round up to next day
            days += 1
        return float(bike.price) * days
    def create(self, validated_data):
        # Get the user from the context
        user = self.context['request'].user
        
        # Calculate total amount
        total_amount = self.calculate_total_amount(
            validated_data['bike'],
            validated_data['pickup_date'],
            validated_data['dropoff_date']
        )
        
        # Create the rental
        rental = BikeRental.objects.create(
            user=user,
            bike=validated_data['bike'],
            pickup_location=validated_data['pickup_location'],
            dropoff_location=validated_data['dropoff_location'],
            pickup_date=validated_data['pickup_date'],
            dropoff_date=validated_data['dropoff_date'],
            payment_status='pending',
            rental_status='active',
            total_amount=total_amount
        )
        
        # Update bike availability
        bike = validated_data['bike']
        bike.isAvailable = False
        bike.status = 'IN_USE'
        bike.save()
        
        return rental
    
    def update(self, instance, validated_data):
        print("validated_data", validated_data)
        # Update the rental instance with validated data
        # if 'payment_method' in validated_data:
        #     payment_method = validated_data.get('payment_method')
        #     if payment_method == 'online' and validated_data.get('payment_status') == 'paid':
        #         validated_data['rental_status'] = 'active'
        #     elif payment_method == 'pickup':
        #         validated_data['rental_status'] = 'active'
        
        # Update the instance
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        instance.save()
        return instance