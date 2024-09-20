from django.contrib import admin

from .models import *

class AdminBike(admin.ModelAdmin):
    list_display = ['id','brand', 'model', 'year', 'color', 'features', 'price', 'description', 'image', 'date']
    search_fields = ['id','brand', 'model', 'year', 'color', 'features', 'price', 'description', 'image', 'date']
    list_filter = ['id','brand', 'model', 'year', 'color', 'features', 'price', 'description', 'image', 'date']


class AdminFeatures(admin.ModelAdmin):
    list_display = ['start', 'engine', 'distance']
    search_fields = ['start', 'engine', 'distance']
    list_filter = ['start', 'engine', 'distance']

admin.site.register(Bike, AdminBike)
admin.site.register(Features, AdminFeatures)

