from django.contrib import admin
from .models import User


class AdminUser(admin.ModelAdmin):
    list_display=['username', 'email', 'first_name', 'last_name', 'is_active']
    ordering = ('-date_joined',)
    


admin.site.register(User,AdminUser)