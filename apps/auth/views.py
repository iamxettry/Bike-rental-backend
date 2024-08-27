from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
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
                response.set_cookie(key="Auth_token", value=tokens['access'],max_age=3600, httponly=True,secure=False, samesite='lax')
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
        