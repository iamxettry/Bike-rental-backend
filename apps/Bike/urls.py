
from django.contrib import admin
from django.urls import path, include
from .views import *

urlpatterns = [
    path('create/', BikeCreateView.as_view(), name='create'),
    path('lists/', BikeListView.as_view(), name='bike-list' )
]

