from django.urls import path
from .views import *
urlpatterns = [
    path('register/user/', RegisterUserView.as_view(), name="Register-user" )
]