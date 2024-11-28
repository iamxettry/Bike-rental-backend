
from django.contrib import admin
from django.urls import path, include
from .views import *

urlpatterns = [
    path('create/', BikeCreateView.as_view(), name='create'),
    path('lists/', BikeListView.as_view(), name='bike-list' ),
    path('retrieve/<uuid:pk>/', BikeRetriveView.as_view(), name='bike-retrieve'),
    path('update/<uuid:pk>/', BikeUpdateView.as_view(), name='bike-update'),
    path('update-status/<uuid:pk>/', BikeStatusUpdateView.as_view(), name='bike-update-status'),
    path('featured/', FeaturedBikeListView.as_view(), name='featured-bike'),
    path('search/', BikeSearchView.as_view(), name='bike-search'),
    path('delete/<uuid:pk>/', BikeDeleteView.as_view(), name='bike-delete'),
    path('rating/', BikeRatingView.as_view(), name='rating'),
    path('location/<uuid:pk>/', BikeLocationView.as_view(), name='locations'),
]

