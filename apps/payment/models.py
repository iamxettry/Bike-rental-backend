from django.db import models
from uuid import uuid4
from apps.Bike_rent.models import BikeRental 
from apps.auth.models import User

class Payment(models.Model):
    PAYMENT_METHOD_CHOICES = [
        ('online', 'Online'),
        ('offline', 'Offline')
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rental = models.ForeignKey(BikeRental, on_delete=models.CASCADE, related_name="payments")  
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, default='online')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    remaining_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    payment_date = models.DateTimeField(auto_now_add=True)
    
    # Optional fields for transaction reference or payment details
    transaction_id = models.CharField(max_length=255, null=True, blank=True)
    payment_details = models.TextField(null=True, blank=True)
    
    
    def __str__(self):
        return f"Payment {self.id} for Rental {self.rental.id} "

    class Meta:
        ordering = ['-payment_date']
