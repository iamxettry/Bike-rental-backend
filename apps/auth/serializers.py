from rest_framework import serializers
from .models import User

# user register serialzers 
class RegisterSerializers(serializers.ModelSerializers):
    password = serializers.CharField(write_only=True,style={'input_type':'password'})

    class Meta:
        model=User
        fields=['id','first_name','last_name','username','email','password', 'is_active','is_staff','date_joined']

    