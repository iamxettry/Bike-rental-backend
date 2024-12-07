from django.contrib import admin
from .models import Payment

class PaymentAdmin(admin.ModelAdmin):
    list_display = ['id', 'product_id', 'total_amount', 'amount_paid', 'remaining_amount', 'payment_date', 'transaction_id', 'payment_details']
    search_fields = ['product_id', 'total_amount', 'amount_paid', 'remaining_amount', 'payment_date', 'transaction_id', 'payment_details']
    list_filter = ['product_id', 'total_amount', 'amount_paid', 'remaining_amount', 'payment_date', 'transaction_id', 'payment_details']
    list_per_page = 20

admin.site.register(Payment, PaymentAdmin)
