
from rest_framework import serializers, exceptions
from .models import Bike, Features, Rating
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
    average_rating = serializers.SerializerMethodField()
    # features = FeaturesSerializer()

    class Meta:
        model = Bike
        fields = '__all__'
    def get_average_rating(self, obj):
        # Use the `average_rating` method of the Bike model to get the average rating
        return obj.average_rating()
    def validate(self, attrs):
        if not self.partial and attrs.get('price', 0) < 500:
            raise exceptions.APIException("Price should be greater than 500.")
        return super().validate(attrs)

# Rating serializer

class RatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rating
        fields = '__all__'

    def validate(self, attrs):
        if not self.partial and attrs.get('rating', 0) < 1:
            raise exceptions.APIException("Rating should be greater than 1.")
        return super().validate(attrs)