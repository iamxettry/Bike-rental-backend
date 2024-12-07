from rest_framework import generics,status ,exceptions
from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from rest_framework.decorators import action
from .serializers import InitiatePaymentSerializer,VerifyPaymentSerializer,EsewaPaymentRequestSerializer,EsewaPaymentNotificationSerializer, EsewaPaymentSerializer
from .models import Payment
from .utils import generate_transaction_id, get_esewa_url, generate_esewa_form_data
import requests
from django.conf import settings

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

    @action(detail=False, methods=['post'])
    def initiate(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            # Create payment record
            payment = serializer.save(
                transaction_id=generate_transaction_id(),
                status='PENDING'
            )
            
            # Generate eSewa form data
            form_data = generate_esewa_form_data(payment)
            esewa_url = get_esewa_url()
            
            return Response({
                'payment_url': esewa_url,
                'form_data': form_data,
                'transaction_id': payment.transaction_id
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def verify(self, request):
        ref_id = request.query_params.get('refId')
        transaction_id = request.query_params.get('oid')
        
        if not ref_id or not transaction_id:
            return Response({
                'message': 'Missing required parameters'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        payment = get_object_or_404(Payment, transaction_id=transaction_id)
        
        # Verify with eSewa
        verify_url = "https://uat.esewa.com.np/epay/transrec"  # Use prod URL in production
        data = {
            'amt': payment.amount,
            'rid': ref_id,
            'pid': payment.product_id,
            'scd': settings.ESEWA_SCD
        }
        
        response = requests.post(verify_url, data=data)
        
        if response.status_code == 200 and "Success" in response.text:
            payment.status = 'SUCCESS'
            payment.save()
            return Response({
                'message': 'Payment verified successfully',
                'status': payment.status
            })
        
        payment.status = 'FAILED'
        payment.save()
        return Response({
            'message': 'Payment verification failed',
            'status': payment.status
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
