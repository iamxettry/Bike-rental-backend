from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.exceptions import ValidationError
from apps.Bike.models import Bike
from apps.common.models import Location
from apps.Bike.serializers import BikeSerializer
# Create your views here.

# Views to search Bike on locations
class BikeSearchView(APIView):
    def post(self, request):
        location_id = request.data.get('pickup_location')
        if not location_id:
            return Response({'detail': 'location is required'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            location = Location.objects.get(id=location_id)
        except Location.DoesNotExist:
            return Response({'detail': 'location not found'}, status=status.HTTP_400_BAD_REQUEST)
        bikes = Bike.objects.filter(locations=location)
        
        if bikes.exists():
            # Serialize the bikes data
            serializer = BikeSerializer(bikes, many=True)
            return Response({'success':'Avialable Bike list .', "data":serializer.data }, status=status.HTTP_200_OK)
        else:
            return Response({'detail': 'No bikes available at this location'}, status=status.HTTP_200_OK)
