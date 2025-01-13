from rest_framework import generics,status ,exceptions
from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.shortcuts import get_object_or_404
from rest_framework.decorators import action
from .serializers import InitiatePaymentSerializer,VerifyPaymentSerializer,EsewaPaymentRequestSerializer,EsewaPaymentNotificationSerializer, EsewaPaymentSerializer, PaymentSerializer
from .models import Payment
from .utils import generate_transaction_id, get_esewa_url, generate_esewa_form_data
import requests
from django.conf import settings
from apps.Bike_rent.models import BikeRental
import calendar
from django.utils import timezone
from uuid import UUID
from django.db.models import Sum

import re

class InitiatePaymentView(generics.GenericAPIView):
    serializer_class = InitiatePaymentSerializer
    permission_classes = [IsAuthenticated]
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            response = serializer.validated_data.get('response')
            if not response:
                return Response({"detail": "No response received from payment gateway"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            return Response(response, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class VerifyPaymentView(generics.GenericAPIView):
    serializer_class = VerifyPaymentSerializer

    def post(self, request, *args, **kwargs):
        pidx = request.data.get('pidx')
        if not pidx:
            return Response({"error": "pidx not provided"}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(data={'pidx': pidx})
        if serializer.is_valid(raise_exception=True):
        
            response = serializer.validated_data.get('response')
            if not response:
                return Response({"detail": "No response received from payment gateway"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            return Response(response,status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    


# E-Sewa views 

class EsewaPaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = EsewaPaymentSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['post'])
    def initiate(self, request):
        bike_rental_id = request.data.get('product_id')
        try:
            bike_rental = BikeRental.objects.get(id=bike_rental_id)
            request.data['product_id'] = bike_rental.id
        except BikeRental.DoesNotExist:
            return Response({
                'error': 'Invalid bike rental ID'
            }, status=status.HTTP_400_BAD_REQUEST)


        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            # Create payment record
            payment = serializer.save(
                transaction_id=generate_transaction_id(),
                status='pending'
            )
            
            # Generate eSewa form data
            form_data = generate_esewa_form_data(payment)
            esewa_url = get_esewa_url()
            
            return Response({
                'payment_url': esewa_url,
                'form_data': form_data,
                'transaction_id': payment.transaction_id,
                'remaining_amount': payment.remaining_amount
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def verify(self, request):
        """
        Verify eSewa payment with parameters matching frontend implementation
        """
        oid = request.data.get('oid')
        amt = request.data.get('amt')
        ref_id = request.data.get('refId')
        rental_id = request.data.get('rentalId')
        print(f"Received transaction ID (oid): {oid}")
        print(f"Verify payment request data: {request.data}")
        try:
            UUID(oid)  # This will raise an exception if `oid` is not a valid UUID
        except ValueError:
            return Response({
        'success': False,
        'message': 'Invalid transaction ID format. Must be a valid UUID.'
         }, status=status.HTTP_400_BAD_REQUEST)
        if not all([oid, amt, ref_id]):
            return Response({
                'success': False,
                'message': 'Missing required parameters'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Get payment using the oid (transaction_id)
            try:
                payment = Payment.objects.get(transaction_id=oid)
                print(f"Found payment: {payment.id} with transaction_id: {payment.transaction_id}")  
            except Payment.DoesNotExist:
                # Log all payments for debugging
                all_payments = Payment.objects.all().values('id', 'transaction_id')
                return Response({
                    'success': False,
                    'message': f"No payment found with transaction_id: {oid}",
                    'debug_info': {
                        'received_oid': oid,
                        'all_transaction_ids': list(all_payments)
                    }
                }, status=status.HTTP_404_NOT_FOUND)
            # Verify with eSewa
            verify_url = "https://uat.esewa.com.np/epay/transrec"  # Use prod URL in production
            data = {
                'amt': amt,
                'rid': ref_id,
                'pid': oid,
                'scd': settings.ESEWA_SCD
            }
            response = requests.post(verify_url, data=data)
            print(f"eSewa verification response: {response.text}")
            if response.status_code == 200 and "Success" in response.text:
                payment.status = 'SUCCESS'
                payment.save()
                print("product id", payment.product_id.id)
                # Update bike rental status if needed
                try:
                    bike_rental = BikeRental.objects.get(id=payment.product_id.id)
                    print("bike rental",bike_rental)
                    bike_rental.payment_status = 'paid'  # Add appropriate status field
                    bike_rental.save()
                    print("bike rental2",bike_rental)

                except BikeRental.DoesNotExist:
                    print(f"BikeRental not found with ID: {rental_id}")
                    pass  # Handle as needed
                
                return Response({
                    'success': True,
                    'message': 'Payment verified successfully',
                    'status': payment.status,
                })
            
            payment.status = 'FAILED'
            payment.save()
            return Response({
                'success': False,
                'message': 'Payment verification failed',
                'status': payment.status
            }, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            print(f"Unexpected error during verification: {str(e)}")
            return Response({
                'success': False,
                'message': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
class EsewaRequestView(APIView):
    def post(self, request):
        serializer = EsewaPaymentRequestSerializer(data=request.data, context={"request":request})
        if serializer.is_valid(raise_exception=True):
            response = serializer.validated_data.get('response')
            if response.status_code == 200:
                html_content= response.text;
                match = re.search(r'action="(https?://[^\s]+)"', html_content)
                if match:
                    redirect_url = match.group(1)
                    return Response({'message': 'Payment initiated successfully', 'redirect_url': redirect_url}, status=status.HTTP_200_OK)
                else:
                    return Response({'message': 'Payment initiated successfully. Please check your browser for further instructions.', 'html_content': html_content}, status=status.HTTP_200_OK)
            else:
                return Response({'message': 'Failed to initiate payment'}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




class PaymentNotificationView(APIView):
    def post(self, request):
        serializer = EsewaPaymentNotificationSerializer(data=request.data)
        if serializer.is_valid():
            # Process payment notification and update order status
            amount = serializer.validated_data['amount']
            txn_id = serializer.validated_data['txn_id']
            status = serializer.validated_data['status']
            order_id = serializer.validated_data['order_id']

            if status == 'Success':
                # Handle successful payment
                return Response({'message': 'Payment successful'}, status=status.HTTP_200_OK)
            else:
                # Handle failed payment
                return Response({'message': 'Payment failed'}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Payment Quick stats
class PaymentStatsView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]
    def get(self, request):
        total_payments = Payment.objects.count()
        pending_payments = Payment.objects.filter(status='PENDING').count()
        successful_payments = Payment.objects.filter(status='SUCCESS').count()
        failed_payments = Payment.objects.filter(status='FAILED').count()
        return Response({
            'total_payments': total_payments,
            'pending_payments': pending_payments,
            'successful_payments': successful_payments,
            'failed_payments': failed_payments,
        }, status=status
        .HTTP_200_OK)
    

# Graph to show monthly payment stats
class MonthlyPaymentStatsView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]
    def get(self, request, *args, **kwargs):
        data = self.get_monthly_revenue_rental_count()
        return Response(data, status=status.HTTP_200_OK)

    def get_monthly_revenue_rental_count(self):
        # Get year wise rental count
        year = self.request.query_params.get('year', timezone.now().year)
        status_filter = self.request.query_params.get('status', 'paid')
        data = []
        for month in range(1, 13):
            rentals = BikeRental.objects.filter(pickup_date__month=month,payment_status=status_filter , pickup_date__year=year)
            amount = rentals.aggregate(total_revenue=Sum('total_amount'))['total_revenue'] or 0
            data.append({
                'month': calendar.month_abbr[month],
                'rentals': rentals.count(),
                'amount': amount
            })
        return data
      

# Get payment list 
class PaymentListView(generics.ListAPIView):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
    def get_queryset(self):
        status = self.request.query_params.get('status')
        if status:
            return Payment.objects.filter(status=status)
        return Payment.objects.all()
    
    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    
# get payment history of user 
class UserPaymentView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        payments = Payment.objects.filter(user=request.user)
        serializer = PaymentSerializer(payments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
        