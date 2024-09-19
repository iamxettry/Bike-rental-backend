from django.contrib import admin

from .views import *

class AdminBike(admin.ModelAdmin):
    list_display = ['id','brand', 'model', 'year', 'color', 'start', 'price', 'description', 'image', 'date']
    search_fields = ['id','brand', 'model', 'year', 'color', 'start', 'price', 'description', 'image', 'date']
    list_filter = ['id','brand', 'model', 'year', 'color', 'start', 'price', 'description', 'image', 'date']

admin.site.register(Bike, AdminBike)

