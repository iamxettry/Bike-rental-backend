
from rest_framework import serializers, exceptions
from .models import Bike, Features


class FeaturesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Features
        fields = ['start', 'engine', 'distance']
class BikeSerializer(serializers.ModelSerializer):
    features = FeaturesSerializer()
    class Meta:
        model = Bike
        fields = '__all__'

    def validate(self, attrs):
        if attrs['price'] < 100:
            raise exceptions.APIException("Price should be greater than 100.")
        return super().validate(attrs)
    
    def create(self, validated_data):
        # Extract features data
        features_data = validated_data.pop('features')
        
        # Create the features instance
        features = Features.objects.create(**features_data)
        
        # Create the bike with the features instance
        bike = Bike.objects.create(features=features, **validated_data)
        return bike
    def update(self, instance, validated_data):

        features_data = validated_data.pop('features', None)
        
        if features_data:
            # Update the features instance
            Features.objects.filter(pk=instance.features.pk).update(**features_data)
        if validated_data.get('price') < 100:
            raise exceptions.APIException("Price should be greater than 100.")

        return super().update(instance, validated_data)
