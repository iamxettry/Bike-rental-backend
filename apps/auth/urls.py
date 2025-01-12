from django.urls import path, include
from .views import *
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'roles', GroupViewSet, basename='role')
router.register(r'permissions', PermissionViewSet, basename='permission')

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

    # admin
    path('login/admin/', LoginAdminView.as_view(), name="Login-admin" ),
    path('user-dashboard/', UserDashboardView.as_view(), name="user-dashboard" ),
    path('user-growth-grpah/', UserGrowthGraphView.as_view(), name="user-growth-graph" ),
    path('user-search/', SearchUserView.as_view(), name="user-search" ),

    path('', include(router.urls)),
]