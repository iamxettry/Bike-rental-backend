from rest_framework import serializers, exceptions
from .models import User
from .utils import generate_userName, CustomPasswordValidator
from django.contrib.auth.hashers import make_password
# user register serialzers 
class RegisterSerializers(serializers.ModelSerializer):
    first_name=serializers.CharField(error_messages={'required':'Fist Name is required', 'blank':'First name cannot not be blank.'})
    password = serializers.CharField(write_only=True,style={'input_type':'password'},
                                     error_messages={
                                         'required':"Password is required.",
                                         'blank':"Password cannot be blank.",
                                     })

    class Meta:
        model=User
        fields=['id','first_name','last_name','username','email','password', 'is_active','is_staff','date_joined']

    def validate_password(self, value):
        validator = CustomPasswordValidator()
        validator(value)
        return value
    def validate(self, attrs):
        password = attrs.get('password')
      
        if len(password) <8 :
            raise exceptions.APIException("Password must be at least 8.")
        return super().validate(attrs)
    
    def create(self, validated_data):
        password = validated_data.pop('password', None)
        user : User = User.objects.create_user(
                first_name=validated_data['first_name'],
                last_name=validated_data['last_name'],
                username=generate_userName(validated_data['first_name'],validated_data['last_name']),
                email=validated_data['email'],
                password=password,
            )
        if password:
            user.password = make_password(password)  # Hash the password
            user.save()
        return user


# Login Serializers 

class LoginUserSerializers(serializers.ModelSerializer):
    email = serializers.EmailField(error_messages={
        'required':"Email is required.",
        'blank':"Email cannot be blank.",

    })
    password = serializers.CharField(style={'input_type':'password'},error_messages={
        'required':"Password is required.",
        'blank':"Password cannot be blank.",
        
    })
    class Meta:
        model=User
        fields=['email','password']

    
    def validate(self, attrs):
        email = attrs.get('email')
        password= attrs.get('password')

        if email and password:
            try :
               user = User.objects.get(email=email)
               if user.check_password(password):
                   return {'user':user}
               else:
                   raise exceptions.APIException("Invalid Credentials!")
            except User.DoesNotExist:
                raise exceptions.APIException("User doesnot exists")
        else:
            raise exceptions.APIException("Invalid Credentials!")