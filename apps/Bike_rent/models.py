from django.db import models
from datetime import datetime, timedelta
from django.core.exceptions import ValidationError
from django.utils import timezone
from apps.Bike.models import Bike
from apps.auth.models import User
import uuid

# Create your models here.
class BikeRental(models.Model):
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded')
    ]
    
    RENTAL_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('overdue', 'Overdue')
    ]
    PAYMENT_METHOD_CHOICES = [
        ('online', 'Online'),
        ('pickup', 'Pay at Pickup'),
        ('dropoff', 'Pay at Dropoff'),
        ('partial', 'Partial Payment')
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    bike = models.ForeignKey(Bike, on_delete=models.PROTECT)
    pickup_location = models.CharField(max_length=255)
    dropoff_location = models.CharField(max_length=255)
    pickup_date = models.DateTimeField()
    dropoff_date = models.DateTimeField()
    actual_dropoff_date = models.DateTimeField(null=True, blank=True)
    
    # Payment and status tracking
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, default='online')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    rental_status = models.CharField(max_length=20, choices=RENTAL_STATUS_CHOICES, default='pending')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Additional tracking fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    payment_date = models.DateTimeField(null=True, blank=True)
    
    def clean(self):
        if self.rental_status == 'completed' and self.payment_status != 'paid':
            raise ValidationError("Rental cannot be marked as completed without payment.")
    #     # Validation to ensure dropoff date is after pickup date
    #     if self.dropoff_date <= self.pickup_date:
    #         raise ValidationError("Dropoff date must be after pickup date")
        
    #     # Validation to ensure pickup date is not in the past
    #     if not self.pk:  # If the object does not have a primary key, it's being created
    #         if self.pickup_date < timezone.now():
    #             raise ValidationError("Pickup date cannot be in the past.")
    
    def calculate_total_amount(self):
        """Calculate the total rental amount based on duration and bike category rate"""
        duration = self.dropoff_date - self.pickup_date
        return round(float(self.bike.price) * duration, 2)
    
    def save(self, *args, **kwargs):
        # Calculate total amount before saving
        if not self.total_amount:
            self.total_amount = self.calculate_total_amount()
        
        # # Update bike status
        # if not self.rental_status or self.rental_status in ['pending', 'active']:
        #     if self.payment_status == 'paid' or (
        #      self.payment_method == 'pickup' and self.payment_status != 'failed'
        # ):
        #         self.rental_status = 'active'
    
    # If rental is completed or cancelled, update bike condition
        if self.rental_status in ['completed', 'cancelled']:
             self.bike.status = 'AVAILABLE'
        
        self.bike.save()
        super().save(*args, **kwargs)
    
    def is_expired(self):
        """Check if the rental is expired"""
        return timezone.now() > self.dropoff_date
    
    def __str__(self):
        return f"Rental {self.id} - {self.user.username} - {self.bike.name}"

    class Meta:
        ordering = ['-created_at']