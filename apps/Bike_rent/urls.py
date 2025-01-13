
from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *

router = DefaultRouter()
router.register(r'bike', BikeRentalViewSet, basename='rental')
urlpatterns = [
    path('bike-search/', BikeSearchView.as_view(), name='bike-search'),
    path('', include(router.urls)),
    path('bike/update/<uuid:pk>/', BikeRentUpdateView.as_view(), name='bike-update' ),
    path('bike/admin/update/<uuid:pk>/', BikeRentAdminUpdateView.as_view(), name='bike-admin-update' ),
    path('rentals/', BikeRentalListView.as_view(), name='rental-list'),
    path('rentals-stats/', BikeRentalStatsView.as_view(), name='rental-stats'),
    path('my-rentals/', UserRentalsView.as_view(), name='my-rentals'),
]

