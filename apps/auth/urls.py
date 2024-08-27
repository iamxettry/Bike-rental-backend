from django.urls import path
from .views import *
urlpatterns = [
    path('register/user/', RegisterUserView.as_view(), name="Register-user" ),
    path('login/user/', LoginUserView.as_view(), name="Login-user" ),
    path('login/user/verify-otp/', VefifyLoginOTPView.as_view(), name="Login-user-otp" ),
    path('resend-otp/', ResendOtpView.as_view(), name="resend-otp" ),
    path('logout/user/', UserLogOutView.as_view(), name="logout-user" ),
    path('change-password/', UserChangePasswordView.as_view(), name="change-password" ),
    path('forgot-password/', ForgotPasswordView.as_view(), name="forgot-password" ),
    path('forgot-password/verify-otp/', VefiryForgotPasswordView.as_view(), name="forgot-password-otp-verify" ),
    path('forgot-password/change-password/', ChangeForgotPasswordView.as_view(), name="forgot-password-change" ),
    path('user/details/', UserDetailView.as_view(), name="user-details" ),
    path('users/list/', UserList.as_view(), name="users-list" ),
    path('user/retrieve/<uuid:pk>/', UserRetrieve.as_view(), name="user-retrieve" ),
]