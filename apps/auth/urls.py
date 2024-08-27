from django.urls import path
from .views import *
urlpatterns = [
    path('register/user/', RegisterUserView.as_view(), name="Register-user" ),
    path('login/user/', LoginUserView.as_view(), name="Login-user" ),
    path('login/user/verify-otp/', VefifyLoginOTPView.as_view(), name="Login-user-otp" ),
]