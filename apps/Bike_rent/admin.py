from django.contrib import admin

from .models import BikeRental
# Register your models here.

class AdminRentals(admin.ModelAdmin):
    list_display = ['user', 'bike', 'pickup_location', 'dropoff_location', 'pickup_date', 'dropoff_date', 'payment_status', 'rental_status', 'total_amount', 'created_at']

    search_fields = ['user', 'bike', 'pickup_location', 'dropoff_location', 'pickup_date', 'dropoff_date', 'payment_status', 'rental_status', 'total_amount', 'created_at']

    

admin.site.register(BikeRental, AdminRentals)