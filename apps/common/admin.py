from django.contrib import admin

# Register your models here.

from .models import Location, UserActivity

class AdminLocation(admin.ModelAdmin):
    list_display = ['id','city']

class AdminUaserActivity(admin.ModelAdmin):
    list_display=['user','activity', 'timestamp']
admin.site.register(Location, AdminLocation)
admin.site.register(UserActivity, AdminUaserActivity)