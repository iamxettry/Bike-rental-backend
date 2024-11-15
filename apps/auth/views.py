from rest_framework.views import APIView
from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status,permissions
from rest_framework.permissions import IsAdminUser,IsAuthenticated
from .serializers import *
from .models import User
from apps.common.otp import OTPAction, OTPhandlers
from apps.common.utils import get_tokens_for_user
from django.utils import timezone

import os

is_production = os.getenv('DJANGO_ENV') == 'production'
# Register User view 
class RegisterUserView(generics.CreateAPIView):
    serializer_class = RegisterSerializers
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"success": "Register Successfully."}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Login View 
class LoginUserView(generics.CreateAPIView):
    serializer_class = LoginUserSerializers
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
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
                response.set_cookie(
                    key="access_token", 
                    value=tokens['access'],
                    max_age=3600, 
                    httponly=True,
                    secure=is_production, 
                    samesite='None'if is_production else 'lax' 
                    )
                response.set_cookie(
                    key="refresh_token",
                      value=tokens['refresh'], 
                      max_age=3600, httponly=True, 
                      secure=is_production, 
                      samesite='None'if is_production else 'lax' 
                      )
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
class VefifyLoginOTPView(generics.CreateAPIView):
    serializer_class = VerifyLoginOTPSerializer
    def post(self,request):
        serializer=self.get_serializer(data=request.data, context={'request':request})
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
class ResendOtpView(generics.CreateAPIView):
    serializer_class = ResendOTPSerializer
    def post(self, request):
        serializer=self.get_serializer(data=request.data)
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
class UserLogOutView(generics.CreateAPIView):
    serializer_class = UserLogOutSerializer
    def post(self, request):
        refresh_token = request.COOKIES.get('refresh_token')
        if not refresh_token:
            return Response({"error": "Refresh token not found"}, status=status.HTTP_400_BAD_REQUEST)
        serializer=self.get_serializer(data={'refresh': refresh_token})
        if serializer.is_valid():
            try:
                serializer.save()
                response = Response({'success': 'Logged out successfully.'}, status=status.HTTP_200_OK)
                response.delete_cookie('access_token')
                response.delete_cookie('refresh_token')
                
                return response
            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
            
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
    

# userChange Password View 
class UserChangePasswordView(generics.CreateAPIView):
    serializer_class = UserChangePasswordSerializer
    permission_classes=[IsAuthenticated]
    def post(self, request):
        serializer=self.get_serializer(data=request.data, context={'request':request})
        if serializer.is_valid():
            user = request.user
            new_password = serializer.validated_data['new_password']
            user.set_password(new_password)
            user.save()
            return Response({"success":"Password Changed successfully."},status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

# ForgotPassword Views
class ForgotPasswordView(generics.CreateAPIView):
    serializer_class = ForgotPasswordSerializer
    
    def post(self, request):
        serializer=self.get_serializer(data=request.data)

        if serializer.is_valid():
            user= serializer.validated_data.get('user', None)
            otp_handler = OTPhandlers(request,user,OTPAction.RESET)
            success,message,otp_created_at = otp_handler.send_otp()
            if not success:
                return Response({'error': message}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            return Response({"success":"Reset OTP has been sent to your email address."},status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

# Verify Forgot password View
class VefiryForgotPasswordView(generics.CreateAPIView):
    serializer_class = ForgotPasswordVerifySerializer
    def post(self, request):
        serializer = ForgotPasswordVerifySerializer(data=request.data, context={'request':request})

        if serializer.is_valid():
            message = serializer.validated_data.get('message',None)
            return Response({"success":{message}}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        
# ChangeForgot passwordView
class ChangeForgotPasswordView(generics.CreateAPIView):
    serializer_class = ChangeForgotPasswordSerializer
    def post(self, request):
        serializer=self.get_serializer(data=request.data)
        if serializer.is_valid():
            return Response({"success":"Password Changed Successfully."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        

# user Details View
class UserDetailView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permissions_classes=[IsAuthenticated]
    def get_object(self):
        return self.request.user



# user list
class UserList(generics.ListAPIView):
    serializer_class = UserSerializer
    permission_classes=[IsAuthenticated,IsAdminUser]

    def get_queryset(self):
        return User.objects.all()

# user retrieve view
class UserRetrieve(generics.RetrieveAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    def get(self, request, pk):
        user = User.objects.get(id=pk)
        serializer = self.get_serializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

# Login Admin View

class LoginAdminView(generics.CreateAPIView):
    serializer_class = LoginAdminSerializers
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
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
                response.set_cookie(
                    key="access_token", 
                    value=tokens['access'],
                    max_age=3600, 
                    httponly=True,
                    secure=is_production, 
                    samesite='None'if is_production else 'lax' 
                    )
                response.set_cookie(
                    key="refresh_token",
                      value=tokens['refresh'], 
                      max_age=3600, httponly=True, 
                      secure=is_production, 
                      samesite='None'if is_production else 'lax' 
                      )
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