
from rest_framework import serializers, exceptions
from .models import Bike, Features, Rating
from apps.auth.models import User
import json
START_CHOICES = (
    ('SELF_START_ONLY', 'Self Start Only'),
    ('KICK_AND_SELF_START', 'Kick & Self Start'),
    ('KICK_START_ONLY', 'Kick Start Only'),
)

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']


# Rating Post Serializer
class RatingPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rating
        fields = '__all__'
    def validate(self, attrs):
        if not self.partial and attrs.get('rating', 0) < 1:
            raise exceptions.APIException("Rating should be greater than 1.")
        return attrs


# Rating serializer
class RatingSerializer(serializers.ModelSerializer):
    user = UserSerializer()  
    class Meta:
        model = Rating
        fields = ['id','user', 'bike_id', 'rating', 'comment', 'date']

class FeaturesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Features
        fields = ['start', 'engine', 'distance']
class BikeSerializer(serializers.ModelSerializer):
    average_rating = serializers.SerializerMethodField()
    ratings = RatingSerializer(many=True, read_only=True)
    locations = serializers.StringRelatedField(many=True)
    # raging count
    ratings_count = serializers.SerializerMethodField()
    # features = FeaturesSerializer()

    class Meta:
        model = Bike
        fields = '__all__'
    
    def get_ratings_count(self, obj):
        return obj.ratings.count()    #count the number of ratings
    
    def get_average_rating(self, obj):
        return obj.average_rating()   #get the average rating
    def validate(self, attrs):
        if not self.partial and attrs.get('price', 0) < 500:
            raise exceptions.APIException("Price should be greater than 500.")
        return super().validate(attrs)
