
from django.contrib import admin
from django.urls import path, include
from .views import *

urlpatterns = [
    path('bike-search/', BikeSearchView.as_view(), name='bike-search'),
   
]

