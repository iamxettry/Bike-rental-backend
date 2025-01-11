from django.db import models
from uuid import uuid4
from apps.Bike_rent.models import BikeRental 
from apps.auth.models import User
from django.utils import timezone

class Payment(models.Model):
    PAYMENT_STATUS = (
        ('PENDING', 'Pending'),
        ('SUCCESS', 'Success'),
        ('FAILED', 'Failed'),
    )
    PAYMENT_METHOD_USED = [
        ('credit_card', 'Credit Card'),
        ('debit_card', 'Debit Card'),
        ('esewa', 'E-Sewa'),
        ('khalti', 'Khalti'),
        ('cash', 'Cash')
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product_id = models.ForeignKey(BikeRental, on_delete=models.CASCADE, related_name="payments")  
    status = models.CharField(max_length=10, choices=PAYMENT_STATUS, default='PENDING')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    remaining_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    payment_date = models.DateTimeField(auto_now_add=True)

    payment_via = models.CharField(max_length=20, choices=PAYMENT_METHOD_USED, default='cash')

    
    # Optional fields for transaction reference or payment details
    transaction_id = models.CharField(max_length=255, null=True, blank=True,unique=True)
    payment_details = models.TextField(null=True, blank=True)
    
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    def save(self, *args, **kwargs):
        # Auto-calculate remaining amount if not set
        if self.remaining_amount is None:
            self.remaining_amount = self.total_amount - self.amount_paid
        super().save(*args, **kwargs)
        
    def __str__(self):
        return f"Payment {self.id} for Rental {self.product_id.id} "

    class Meta:
        ordering = ['-payment_date']
