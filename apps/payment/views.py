from rest_framework import generics,status ,exceptions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from .serializers import InitiatePaymentSerializer,VerifyPaymentSerializer,EsewaPaymentRequestSerializer,EsewaPaymentNotificationSerializer

import re

class InitiatePaymentView(generics.GenericAPIView):
    serializer_class = InitiatePaymentSerializer
    permission_classes = [IsAuthenticated]
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        response = serializer.validated_data.get('response')
        if not response:
            return Response({"error": "No response received from payment gateway"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response(response, status=status.HTTP_200_OK)
    
class VerifyPaymentView(generics.GenericAPIView):
    serializer_class = VerifyPaymentSerializer

    def post(self, request, *args, **kwargs):
        pidx = request.data.get('pidx')
        if not pidx:
            return Response({"error": "pidx not provided"}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(data={'pidx': pidx})
        serializer.is_valid(raise_exception=True)
        
        response = serializer.validated_data.get('response')
        if not response:
            return Response({"error": "No response received from payment gateway"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response(response,status=status.HTTP_200_OK)
    


# E-Sewa views 

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
