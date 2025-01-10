
from django.contrib import admin
from django.urls import path, include
from .views import *

urlpatterns = [
    path('location-create/', LocationCreateView.as_view(), name='location-create'),
    path('location-list/', LocationListView.as_view(), name='location-create'),
    path('location-retrieve-update-delete/<uuid:pk>/', LocationRetriveUpdateDestroyView.as_view(), name='location-retrieve-update-delete'),
    path('location-retrieve/<uuid:pk>/', LocationRetrive.as_view(), name='location-retrieve'),
    path('location-search/', LocationSearchView.as_view(), name='location-search'),

    # Quick Stats 
    path('quick-stats/', QuickStatsViews.as_view(), name='quick-stats'),
    # Monthly rentals
    path('monthly-rentals/', MonthlyRentalCount.as_view(), name='monthly-rentals'),


]

