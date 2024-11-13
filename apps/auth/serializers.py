from rest_framework import serializers, exceptions
from .models import User
from .utils import generate_userName, CustomPasswordValidator
from django.contrib.auth.hashers import make_password
from apps.common.otp import OTPhandlers, OTPAction
from rest_framework_simplejwt.tokens import RefreshToken
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
        validator.validate(value)
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
        
# VerifyOtp serializers 
class VerifyLoginOTPSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(max_length=255,required=True,allow_blank=False,error_messages={
        'required':'Email is required.',
        'blank':'Email cannot be blank.',
    })
    otp = serializers.CharField(max_length=255,required=True,allow_blank=False,error_messages={
        'required':'Otp is required.',
        'blank':'Otp cannot be blank.'
    })
    class Meta:
        model=User
        fields=['otp','email']

    def validate(self, attrs):
        email=attrs.get('email', None)
        otp=attrs.get('otp',None)

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            attrs['user'] = None
            raise exceptions.APIException("User does not exist")
        
        otp_handlers = OTPhandlers(
            request=self.context['request'],
            user=user,
            action=OTPAction.LOGIN,
        )

        verified,message = otp_handlers.verify_otp(otp)

        if not verified:
            raise exceptions.APIException(message)
        
        attrs['user'] = user
        attrs['message'] = message
        return super().validate(attrs)
    
# Resend Otp Serializers
class ResendOTPSerializer(serializers.ModelSerializer):
    email= serializers.EmailField(max_length=255,required=True,allow_blank=False,error_messages={
        'required':'Email is required.',
        'blank':'Email cannot be blank.',
    })
    class Meta:
        model=User
        fields=['email']

    def validate(self, attrs):
        email= attrs.get('email')
        if not email:
            raise exceptions.APIException("E-mail not found.")
        
        try:
            user=User.objects.get(email=email)
        except User.DoesNotExist:
            raise exceptions.APIException("User Not found.")
        attrs['user']=user
        return super().validate(attrs)
    
#User logout Serializer
class UserLogOutSerializer(serializers.Serializer):
    refresh=serializers.CharField()
 
    def validate(self, attrs):
        self.token = attrs['refresh']
        return attrs

    def save(self, **kwargs):
        try:
            # Blacklist the refresh token
            RefreshToken(self.token).blacklist()
        except Exception as e:
            self.fail('bad_token')

    
# user Change password 
class UserChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(style={'input_type':'password'}, required=True, allow_blank=False,error_messages={
        'required':'Old_password is required.',
        'blank':'Old_password cannot be blank.',
    })
    new_password = serializers.CharField(style={'input_type':'password'}, required=True, allow_blank=False,error_messages={
        'required':'New_password is required.',
        'blank':'New_password cannot be blank.',
    })
    confirm_password = serializers.CharField(style={'input_type':'password'}, required=True, allow_blank=False,error_messages={
        'required':'Confirm_password is required.',
        'blank':'Confirm_password cannot be blank.',
    })

    def validate(self, attrs):
        user = self.context['request'].user
        old_password = attrs.get('old_password')
        new_password=attrs.get('new_password')
        confirm_password=attrs.get("confirm_password")
        if not user:
            raise exceptions.APIException("User not found.")
        
        if not user.check_password(old_password):
            raise exceptions.APIException("Invalid Old password!")

        if new_password!=confirm_password:
            raise exceptions.APIException("New password and Confirm password didnot match.")
        
        validator = CustomPasswordValidator()
        validator.validate(new_password)
        return super().validate(attrs)

# ForgotPassword Serializer 
class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=255,required=True,allow_blank=False,error_messages={
        'required':'Email is required.',
        'blank':'Email cannot be blank.',
    })

    def validate(self, attrs):
        email=attrs.get('email')
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            attrs['user']=None
            raise exceptions.APIException("User doesnot exits.")
        attrs['user']=user
        return super().validate(attrs)
    

# Forgot passwrd vefify password Serializer
class ForgotPasswordVerifySerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=255,required=True,allow_blank=False,error_messages={
        'required':'Email is required.',
        'blank':'Email cannot be blank.',
    })
    otp = serializers.CharField(max_length=255,required=True,allow_blank=False,error_messages={
        'required':'Otp is required.',
        'blank':'Otp cannot be blank.'
    })

    def validate(self, attrs):
        email=attrs.get('email', None)
        otp=attrs.get('otp',None)

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            attrs['user'] = None
            raise exceptions.APIException("User does not exist")
        
        otp_handlers = OTPhandlers(
            request=self.context['request'],
            user=user,
            action=OTPAction.RESET,
        )

        verified,message = otp_handlers.verify_otp(otp)

        if not verified:
            raise exceptions.APIException(message)
        
        attrs['user'] = user
        attrs['message'] = message
        return super().validate(attrs)


# ChangeForgot password Serializers
class ChangeForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField(style={'input_type':'password'}, required=True, allow_blank=False,error_messages={
        'required':'Email is required.',
        'blank':'Email cannot be blank.',
    })
    new_password = serializers.CharField(style={'input_type':'password'}, required=True, allow_blank=False,error_messages={
        'required':'New_password is required.',
        'blank':'New_password cannot be blank.',
    })
    confirm_password = serializers.CharField(style={'input_type':'password'}, required=True, allow_blank=False,error_messages={
        'required':'Confirm_password is required.',
        'blank':'Confirm_password cannot be blank.',
    })

    def validate(self, attrs):
        email= attrs.get("email")
        new_password=attrs.get("new_password")
        confirm_password=attrs.get("confirm_password")
        if new_password!=confirm_password:
            raise exceptions.APIException("New password and Confirm password didnot match.")
        try:
            user = User.objects.get(email=email)
            attrs['user']=user
        except User.DoesNotExist:
            attrs['user']=None
            raise exceptions.APIException("User Does not exits.")
        validator = CustomPasswordValidator()
        validator.validate(new_password)
        user.set_password(new_password)
        user.save()
        return super().validate(attrs)


#user Details
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id','first_name','last_name','username','email', 'profile_picture', 'is_superuser', "is_active"]
    
    def get_profile_picture(self, obj):
        request = self.context.get('request')
        if obj.profile_picture and request:
            return request.build_absolute_uri(obj.profile_picture.url)
        return None
    def update(self, instance, validated_data):
        instance.first_name = validated_data.get('first_name',instance.first_name)
        instance.last_name = validated_data.get('last_name',instance.last_name)
        instance.username = validated_data.get('username',instance.username)
        instance.email = validated_data.get('email',instance.email)
        instance.profile_picture=validated_data.get('profile_picture',instance.profile_picture)
        instance.save()
        return instance 




