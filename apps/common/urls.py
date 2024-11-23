
from django.contrib import admin
from django.urls import path, include
from .views import *

urlpatterns = [
    path('location-create/', LocationCreateView.as_view(), name='location-create'),
    path('location-list/', LocationListView.as_view(), name='location-create'),
    path('location-retrieve-update-delete/<uuid:pk>/', LocationRetriveUpdateDestroyView.as_view(), name='location-retrieve-update-delete'),
]

