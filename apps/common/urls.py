
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
    # Hourly usage
    path('hourly-usage/', HourlyUsagePattern.as_view(), name='hourly-usage'),
    # Bike Status
    path('bike-status/', BikeDistributionStatus.as_view(), name='bike-status'),
    # Monthly Revenue with rentals
    path('monthly-revenue-rentals/', MonthlyRevenueRentalCount.as_view(), name='monthly-revenue'),
    # user activity 
    path('user-activity/', WeaklyUserCount.as_view(), name='user-activity'),
    # Payment methods used stautus
    path('payment-methods-stats/', PaymentMethodsStatsGraph.as_view(), name='payment-stats')

]

