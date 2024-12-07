from django.contrib import admin
from .models import Payment

class PaymentAdmin(admin.ModelAdmin):
    list_display = ['id', 'rental', 'payment_method', 'total_amount', 'amount_paid', 'remaining_amount', 'payment_date', 'transaction_id', 'payment_details']
    search_fields = ['rental', 'payment_method', 'total_amount', 'amount_paid', 'remaining_amount', 'payment_date', 'transaction_id', 'payment_details']
    list_filter = ['rental', 'payment_method', 'total_amount', 'amount_paid', 'remaining_amount', 'payment_date', 'transaction_id', 'payment_details']
    list_per_page = 20

admin.site.register(Payment, PaymentAdmin)
