
from rest_framework import serializers, exceptions
from .models import Bike, Features
import json
START_CHOICES = (
    ('SELF_START_ONLY', 'Self Start Only'),
    ('KICK_AND_SELF_START', 'Kick & Self Start'),
    ('KICK_START_ONLY', 'Kick Start Only'),
)
class FeaturesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Features
        fields = ['start', 'engine', 'distance']
class BikeSerializer(serializers.ModelSerializer):
    # features = FeaturesSerializer()

    class Meta:
        model = Bike
        fields = '__all__'

    def validate(self, attrs):
        if attrs.get('price', 0) < 500:
            raise exceptions.APIException("Price should be greater than 500.")
        return super().validate(attrs)
   