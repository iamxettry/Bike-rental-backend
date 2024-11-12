
from django.contrib import admin
from django.urls import path, include
from .views import *

urlpatterns = [
    path('create/', BikeCreateView.as_view(), name='create'),
    path('lists/', BikeListView.as_view(), name='bike-list' ),
    path('retrieve/<uuid:pk>/', BikeRetriveView.as_view(), name='bike-retrieve'),
    path('update/<uuid:pk>/', BikeUpdateView.as_view(), name='bike-update'),
    path('featured/', FeaturedBikeListView.as_view(), name='featured-bike'),
    path('search/', BikeSearchView.as_view(), name='bike-search'),
]

