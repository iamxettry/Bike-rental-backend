from django.shortcuts import render
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.exceptions import ValidationError
from apps.Bike.models import Bike
from apps.common.models import Location
from apps.Bike.serializers import BikeSerializer
from .serializers import BikeRentalSerializer
from .models import BikeRental
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
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


class BikeRentalViewSet(viewsets.ModelViewSet):
    serializer_class = BikeRentalSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        # Users can only see their own rentals
        return BikeRental.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        # Set the authenticated user and save the rental
        serializer.save(
            user=self.request.user,
            payment_status='pending',
            rental_status='active'
        )
    
    @action(detail=True, methods=['post'])
    def cancel_rental(self, request, pk=None):
        rental = self.get_object()
        
        # Check if rental can be cancelled
        if rental.rental_status not in ['active', 'pending']:
            return Response(
                {"error": "This rental cannot be cancelled"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # If rental hasn't started yet (pickup date is in future)
        if rental.pickup_date > timezone.now():
            rental.rental_status = 'cancelled'
            if rental.payment_status == 'paid':
                rental.payment_status = 'refunded'
            rental.save()
            
            # Make bike available again
            bike = rental.bike
            bike.condition = 'available'
            bike.save()
            
            return Response(
                {"message": "Rental cancelled successfully"},
                status=status.HTTP_200_OK
            )
        else:
            return Response(
                {"error": "Cannot cancel an ongoing rental. Please contact support."},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['get'])
    def active_rentals(self, request):
        active_rentals = self.get_queryset().filter(rental_status='active')
        serializer = self.get_serializer(active_rentals, many=True)
        return Response(serializer.data)


# Views to update bike rent for payment at pickup
@method_decorator(csrf_exempt, name='dispatch')
class BikeRentUpdateView(APIView):
    serializer_class = BikeRentalSerializer
    permission_classes = [IsAuthenticated]

    def patch(self, request, pk):
        try:
            # Get the rental instance
            rental = BikeRental.objects.get(id=pk)
            
            # Check if user is authorized to update this rental
            if rental.user != request.user:
                return Response(
                    {"error": "You are not authorized to update this rental"},
                    status=status.HTTP_403_FORBIDDEN
                )

            # Partial update with the provided data
            serializer = self.serializer_class(
                rental,
                data=request.data,
                partial=True,
                context={'request': request}
            )

            if serializer.is_valid(raise_exception=True):
                serializer.save()
                return Response(
                    {
                        "message": "Confirmed Payment at Pickup",
                        "data": serializer.data,
                        "status": True  
                    },
                    status=status.HTTP_200_OK
                )

        except BikeRental.DoesNotExist:
            return Response(
                {"error": "Rental not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )