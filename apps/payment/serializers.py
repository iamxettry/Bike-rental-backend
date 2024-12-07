from rest_framework import serializers,exceptions
import json
from apps.Bike_rent.models import BikeRental
from apps.auth.models import User
import os
import requests
from uuid import UUID
from .models import Payment
class InitiatePaymentSerializer(serializers.ModelSerializer):
 
    # return_url = serializers.URLField(required=True,
    #     error_messages={
    #         'required': 'Return URL is required.',
    #         'blank': 'Return RUL cannot be blank.',
    #         'invalid': 'Return URL is invalid.'
    #     })


    class Meta:
        model = Payment
        fields = ['id', 'product_id', 'status', 'total_amount', 
            'amount_paid', 'remaining_amount', 'payment_date', 'transaction_id']

    def validate(self, attrs):
        user = self.context['request'].user
        rental_id = attrs.get('rental',None)
        total_amount = attrs.get('total_amount')
        amount_paid = attrs.get('amount_paid')

        # Ensure the amount paid doesn't exceed total amount
        if amount_paid > total_amount:
            raise exceptions.APIException("Amount paid cannot exceed the total amount.")
        
        try:
            UUID(str(rental_id.id))

        except ValueError:
            raise exceptions.APIException("Invalid order UUID")

        try:
            order = BikeRental.objects.get(id=rental_id.id)
        except BikeRental.DoesNotExist:
            raise exceptions.APIException('Bike rent does not exist')
                

        purchase_rental_id = str(order.id)
        purchase_order_name = user.username+"'s Payment"
        amount = float(attrs.get('amount_paid', None))
        # return_url = attrs.get('return_url',None)

        url = f'{os.environ.get("KHALTI_BASE_URL")}epayment/initiate/'

        payload = json.dumps({
            "return_url": os.environ.get('KHALTI_RETUR_URL'),
            "website_url": "http://127.0.0.1:8000",
            "amount": amount,
            "purchase_order_id": purchase_rental_id,
            "purchase_order_name": purchase_order_name,
            "customer_info":{
                "name":f'{user.username} ',
                "email":"test@khalti.com",
                'phone':"9800000001"
            }
        })

        headers = {
            'Authorization': f"key {os.environ.get('KHALTI_SECRET_KEY')}",
            'Content-Type': 'application/json'
        }
        
        response = requests.request("POST",url,headers=headers, data=payload)

        res = {
            "status": response.status_code,
            "message": response.text,
            "result":json.loads(response.text)
        }
        
        # order.pidx = res.get('pidx')
        # order.save()
        
        attrs['response'] = res
        return attrs
    def create(self, validated_data):
        user = self.context['request'].user

        try:
            # crete Payment 
            payment = Payment.objects.create(
                user=user,
                product_id=validated_data['rental'],
                total_amount=validated_data['total_amount'],
                amount_paid=validated_data['amount_paid'],
                remaining_amount=validated_data['total_amount'] - validated_data['amount_paid'],
                payment_date=None,
                transaction_id=None,
                payment_details=None
            )

            return payment
        except BikeRental.DoesNotExist:
            raise exceptions.APIException('Bike rental not found')
        
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        errors = self.errors
        if errors:
            formatted_errors = {field: [message for message in messages] for field, messages in errors.items()}
            return {
                'errors': formatted_errors
            }
        return representation
    
    


class VerifyPaymentSerializer(serializers.Serializer):

    pidx = serializers.CharField(max_length=255, required=True, allow_blank=False, error_messages={
        'required': 'Pidx is required.',
         'blank': 'Pidx cannot be blank.'
    })

    def validate(self, attrs):
        pidx = attrs.get('pidx',None)
        url = f'{os.environ.get("KHALTI_BASE_URL")}epayment/lookup/'

        payload = json.dumps({
            "pidx": pidx,
        })

        headers = {
            'Authorization': f"key {os.environ.get('KHALTI_SECRET_KEY')}",
            'Content-Type': 'application/json'
        }

        response = requests.request("POST",url,headers=headers,data=payload)

        res = json.loads(response.text)

        print("status",res)
        if res.get('status')!= 'Completed':
            raise exceptions.APIException(res.get('status'))
        
        try:
            order = BikeRental.objects.get(pidx=pidx)
        except BikeRental.DoesNotExist:
            raise exceptions.APIException('Payment for this order, not found')
        
        order.payment_status = "paid"
        order.paid_amount = f"{res.get('total_amount')}-{res.get('fee')}"
        order.save()
        attrs['response']=res
        return attrs
    

# E-sewa serializers 

class EsewaPaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ['id', 'total_amount','amount_paid','remaining_amount', 'product_id',  'transaction_id', 'status', 'created_at']
        read_only_fields = ['status', 'transaction_id', 'created_at']

class EsewaPaymentRequestSerializer(serializers.Serializer):
    amount = serializers.DecimalField(max_digits=10, decimal_places=2,
             error_messages={
            'required': 'Amount is required.',
            'blank': 'Amount  cannot be blank.',
            'invalid': 'Amount must be a valid number.'
        })
    rental_id = serializers.CharField(max_length=100)

    def validate(self, attrs):
        request = self.context.get('request')
        rental_id = attrs.get('rental_id',None)
        amount= attrs.get('amount', None)
        print("ser", amount)
        try:
            UUID(str(rental_id))
        except ValueError:
            raise exceptions.APIException("Invalid BikeRental UUID")
        
        try:
            order = BikeRental.objects.get(id=rental_id)
        except BikeRental.DoesNotExist:
            raise exceptions.APIException("BikeRental Not found.")
        if amount <0:
            raise exceptions.APIException("Amount must be valid number")
        

        params = {
                'amt': amount,
                'pdc': 0,
                'txAmt': 0,
                'psc': 0,
                'pcc': 0,
                'tAmt': amount,
                'pid': rental_id,
                'scd': os.environ.get('ESEWA_MERCHANT_ID'),
                'su': request.build_absolute_uri('/api/payment_success/'),
                'fu': request.build_absolute_uri('/api/payment_failed/'),
            }
        response = requests.post(os.environ.get('ESEWA_URL'), data=params)    
        attrs['response'] = response
        return attrs

class EsewaPaymentNotificationSerializer(serializers.Serializer):
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    txn_id = serializers.CharField(max_length=100)
    status = serializers.CharField(max_length=20)
    rental_id = serializers.CharField(max_length=100)
