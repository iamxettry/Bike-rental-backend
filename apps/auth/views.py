from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status,permissions
from rest_framework_simplejwt.tokens import TokenError, RefreshToken
from .serializers import *
from .models import User
from apps.common.otp import OTPAction, OTPhandlers
from apps.common.utils import get_tokens_for_user
from django.utils import timezone
# Register User view 
class RegisterUserView(APIView):
    
    def post(self, request):
        serializer = RegisterSerializers(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"success": "Register Successfully."}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Login View 
class LoginUserView(APIView):
    def post(self, request):
        serializer = LoginUserSerializers(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            if user is None:
                raise exceptions.AuthenticationFailed("User doesnot exist!.")
            
            if user.email_verified :
                user.is_active=True
                user.last_login=timezone.now()
                user.save()
                tokens=get_tokens_for_user(user)
                response=Response({'success':'logged in successfully.'}, status=status.HTTP_200_OK)
                response.set_cookie(key="access_token", value=tokens['access'],max_age=3600, httponly=True,secure=False, samesite='lax')
                response.set_cookie(key="refresh_token", value=tokens['refresh'], max_age=3600, httponly=True, secure=False, samesite='Lax')
                return  response
            else:
                otp_handler= OTPhandlers(request, user, OTPAction.LOGIN)
                success, message,otp_created_at = otp_handler.send_otp()
                if not success:
                    return Response({'error': message}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                return Response({
                    'success':'Login OTP has been sent to your email address',
                    'otp_created_at': otp_created_at.isoformat()
                    
                     },status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# loginOTP Verification View 
class VefifyLoginOTPView(APIView):
    def post(self,request):
        serializer=VerifyLoginOTPSerializer(data=request.data, context={'request':request})
        if serializer.is_valid():
            user = serializer.validated_data.get('user',None)
            message = serializer.validated_data.get('message',None)
            if user is not None:
                tokens = get_tokens_for_user(user)

                user.is_active = True
                user.last_login = timezone.now()
                user.save()
                response=Response({'success':'OTP verified successfully.'}, status=status.HTTP_200_OK)
                response.set_cookie(key="access_token", value=tokens['access'],max_age=3600, httponly=True,secure=False, samesite='lax')
                response.set_cookie(key="refresh_token", value=tokens['refresh'], max_age=3600, httponly=True, secure=False, samesite='Lax')
                return response
            return Response({'error':'OTP verification failed.'},status=status.HTTP_400_BAD_REQUEST) 
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Resend OTP View 
class ResendOtpView(APIView):
    def post(self, request):
        serializer= ResendOTPSerializer(data=request.data)
        if serializer.is_valid():
            user=serializer.validated_data.get('user',None)
            if user is None:
                raise exceptions.AuthenticationFailed("User doesnot exist!.")
            otp_handler= OTPhandlers(request, user, OTPAction.LOGIN)
            success, message,otp_created_at = otp_handler.send_otp()
            if not success:
                return Response({'error': message}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            return Response({
                'success':' OTP has been sent to your email address',
                'otp_created_at': otp_created_at.isoformat()
                
                    },status=status.HTTP_200_OK)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)

# User Logout View
class UserLogOutView(APIView):
    permission_classes=[permissions.IsAuthenticated]
    def post(self, request):
        refresh_token = request.COOKIES.get('refresh_token')
        if not refresh_token:
            return Response({"error": "Refresh token not found"}, status=status.HTTP_400_BAD_REQUEST)
        serializer= UserLogOutSerializer(data={'refresh': refresh_token})
        if serializer.is_valid():
            try:
                response = Response({'success': 'Logged out successfully.'}, status=status.HTTP_200_OK)
                response.delete_cookie('access_token')
                response.delete_cookie('refresh_token')
                
                return response
            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
            
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
    

# userChange Password View 
class UserChangePasswordView(APIView):
    permission_classes=[permissions.IsAuthenticated]
    def post(self, request):
        serializer=UserChangePasswordSerializer(data=request.data, context={'request':request})
        if serializer.is_valid():
            user = request.user
            new_password = serializer.validated_data['new_password']
            user.set_password(new_password)
            user.save()
            return Response({"success":"Password Changed successfully."},status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

# ForgotPassword Views
class ForgotPasswordView(APIView):
    
    def post(self, request):
        serializer=ForgotPasswordSerializer(data=request.data)

        if serializer.is_valid():
            user= serializer.validated_data.get('user', None)
            otp_handler = OTPhandlers(request,user,OTPAction.RESET)
            success,message,otp_created_at = otp_handler.send_otp()
            if not success:
                return Response({'error': message}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            return Response({"success":"Reset OTP has been sent to your email address."},status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

# Verify Forgot password View
class VefiryForgotPasswordView(APIView):
    def post(self, request):
        serializer = ForgotPasswordVerifySerializer(data=request.data, context={'request':request})

        if serializer.is_valid():
            message = serializer.validated_data.get('message',None)
            return Response({"success":{message}}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        

