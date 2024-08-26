from rest_framework import serializers, exceptions
from .models import User
from rest_framework.validators import ValidationError
# user register serialzers 
class RegisterSerializers(serializers.ModelSerializer):
    first_name=serializers.CharField(error_messages={'required':'Fist Name is required', 'blank':'First name cannot not be blank.'})
    password = serializers.CharField(write_only=True,style={'input_type':'password'})

    class Meta:
        model=User
        fields=['id','first_name','last_name','username','email','password', 'is_active','is_staff','date_joined']
    def validate(self, attrs):
        passwrod = attrs.get('password')
        print("password", passwrod)
        return super().validate(attrs)
    
    def create(self, validated_data):
        user : User = User.objects.create_user(
                username=validated_data['username'],
                email=validated_data['email'],
                password=validated_data['password'],
            )
        return user