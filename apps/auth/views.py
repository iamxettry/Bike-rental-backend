from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import RegisterSerializers
from .models import User

# Register User view 

class RegisterUserView(APIView):
    
    def post(self, request):
        serializer = RegisterSerializers(data=request.data)
        if serializer.is_valid():
            return Response({"success": "Register Successfully."}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)