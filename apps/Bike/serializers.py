
from rest_framework import serializers, exceptions
from .models import Bike

class BikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bike
        fields = '__all__'

    def validate(self, attrs):
        if attrs['price'] < 100:
            raise exceptions.APIException("Price should be greater than 100.")
        return super().validate(attrs)
    
    def update(self, instance, validated_data):

        if validated_data.get('price') < 100:
            raise exceptions.APIException("Price should be greater than 100.")

        return super().update(instance, validated_data)
