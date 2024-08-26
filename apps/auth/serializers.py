from rest_framework import serializers, exceptions
from .models import User
from rest_framework.validators import ValidationError
from .utils import generate_userName
# user register serialzers 
class RegisterSerializers(serializers.ModelSerializer):
    first_name=serializers.CharField(error_messages={'required':'Fist Name is required', 'blank':'First name cannot not be blank.'})
    password = serializers.CharField(write_only=True,style={'input_type':'password'})

    class Meta:
        model=User
        fields=['id','first_name','last_name','username','email','password', 'is_active','is_staff','date_joined']

    def validate(self, attrs):
        passwrod = attrs.get('password')
        return super().validate(attrs)
    
    def create(self, validated_data):
        user : User = User.objects.create_user(
                first_name=validated_data['first_name'],
                last_name=validated_data['last_name'],
                username=generate_userName(validated_data['first_name'],validated_data['last_name']),
                email=validated_data['email'],
                password=validated_data['password'],
            )
        return user