from django.contrib import admin

# Register your models here.

from .models import FAQ, CustomerSupport, ReportIssue, SystemAlert

admin.site.register(FAQ)
admin.site.register(CustomerSupport)
admin.site.register(ReportIssue)
admin.site.register(SystemAlert)
