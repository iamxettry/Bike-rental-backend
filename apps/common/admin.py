from django.contrib import admin

# Register your models here.

from .models import Location

class AdminLocation(admin.ModelAdmin):
    list_display = ['city']
admin.site.register(Location, AdminLocation)