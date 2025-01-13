from django.shortcuts import render
from rest_framework import status,generics, permissions, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.exceptions import ValidationError
from rest_framework import exceptions
from apps.Bike.models import Bike
from apps.common.models import Location
from apps.Bike.serializers import BikeSerializer
from .serializers import BikeRentalSerializer
from .models import BikeRental
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from apps.payment.models import Payment
from rest_framework.filters import SearchFilter
from django.db.models import Q
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
            bike.status = 'available'
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
    
    @action(detail=True, methods=['post'])
    def reserve_bike(self, request, pk=None):
        rental = self.get_object()
        bike = rental.bike
        
        if bike.status == 'available':
            bike.status = 'reserved'
            bike.save()
            rental.rental_status = 'pending'
            rental.save()
            return Response({"message": "Bike reserved successfully."}, status=status.HTTP_200_OK)
        
        return Response({"error": "Bike is not available for reservation."}, status=status.HTTP_400_BAD_REQUEST)
    
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
            if rental.user != request.user and not request.user.is_superuser:
                raise exceptions.APIException("You are not authorized to update this rental")
               
            if rental.payment_status == 'paid':
                raise exceptions.APIException("Payment has already been made for this rental")
            # Partial update with the provided data
            serializer = self.serializer_class(
                rental,
                data=request.data,
                partial=True,
                context={'request': request}
            )

            if serializer.is_valid(raise_exception=True):
                payment = Payment.objects.create(
                    user=request.user,
                    product_id=rental,
                    total_amount=rental.total_amount,
                    amount_paid=0.0,  # Assuming initial amount paid is 0 for cash payments
                    remaining_amount=rental.total_amount,
                    payment_via="cash"
                )
                serializer.save(payment_method="pickup", payment_status="pending", rental_status="active")
                return Response(
                    {
                        "message": "Confirmed Payment at Pickup",
                        "payment_details": {
                            "id": payment.id,
                            "status": payment.status,
                            "payment_method": payment.payment_via,
                        },
                        "rental_data": serializer.data,
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
@method_decorator(csrf_exempt, name='dispatch')
class BikeRentAdminUpdateView(APIView):
    serializer_class = BikeRentalSerializer
    permission_classes = [IsAuthenticated, permissions.IsAdminUser]

    def patch(self, request, pk):
        try:
            # Get the rental instance
            rental = BikeRental.objects.get(id=pk)

            print("requested data", self.request.data)
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
                        "message": "Updated Successfully",
                        "rental_data": serializer.data,
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

class BikeRentalListView(generics.ListAPIView):
    serializer_class = BikeRentalSerializer
    # permission_classes = [IsAuthenticated]
    filter_backends = [SearchFilter]
    search_fields = ['id', 'user__username', 'user__email', 'bike__name']

    def get_queryset(self):
        # Retrieve query parameters
        rental_filter = self.request.query_params.get('rental', 'all')
        rental_status = self.request.query_params.get('rental_status', None)
        payment_status = self.request.query_params.get('payment_status', None)
        search_query = self.request.query_params.get('search', None)

        # Base queryset
        queryset = BikeRental.objects.all()

        # Filter by rental type
        if rental_filter == 'active':
            queryset = queryset.filter(rental_status='active')
        elif rental_filter == 'history':
            queryset = queryset.filter(rental_status__in=['completed', 'cancelled'])

        # Filter by rental_status
        if rental_status:
            queryset = queryset.filter(rental_status=rental_status)

        # Filter by payment_status
        if payment_status:
            queryset = queryset.filter(payment_status=payment_status)

        # Apply search filter
        if search_query:
            queryset = queryset.filter(
                Q(id__icontains=search_query) |
                Q(user__username__icontains=search_query) |
                Q(user__email__icontains=search_query) |
                Q(bike__name__icontains=search_query)
            )

        return queryset

# bike rental quick stats
class BikeRentalStatsView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]
    def get(self, request):
        total_rentals = BikeRental.objects.count()
        active_rentals = BikeRental.objects.filter(rental_status='active').count()
        pending_rentals = BikeRental.objects.filter(rental_status='pending').count()
        completed_rentals = BikeRental.objects.filter(rental_status='completed').count()
        cancelled_rentals = BikeRental.objects.filter(rental_status='cancelled').count()
        overdue = BikeRental.objects.filter(rental_status='overdue').count()
        return Response({
            "total_rentals": total_rentals,
            "active_rentals": active_rentals,
            "pending_rentals": pending_rentals,
            "completed_rentals": completed_rentals,
            "cancelled_rentals": cancelled_rentals,
            "overdue_rentals": overdue
        }, status=status.HTTP_200_OK)
    
# View to get active rentals of a user
class UserRentalsView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        active_rentals = BikeRental.objects.filter(user=request.user)
        serializer = BikeRentalSerializer(active_rentals, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)