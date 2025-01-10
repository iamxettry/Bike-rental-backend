from django.db import models
import uuid
from django.db.models import Avg
from apps.common.models import Location
START_CHOICES = (
    ('SELF_START_ONLY', 'Self Start Only'),
    ('KICK_AND_SELF_START', 'Kick & Self Start'),
    ('KICK_START_ONLY', 'Kick Start Only'),
)
STATUS_CHOICES = (
    ('AVAILABLE', 'Available'),
    ('MAINTENANCE', 'Maintenance'),
    ('IN_USE', 'In Use'),
    ('RESERVED', 'Reserved'),
)

class Features(models.Model):
    start = models.CharField(max_length=100, choices=START_CHOICES, default='SELF START ONLY') 
    engine = models.CharField(max_length=100, null=True, blank=True) 
    distance = models.CharField(max_length=100, null=True, blank=True)  

    def __str__(self):
        return f"{self.engine}, {self.distance}, {self.start}"
# Create your models here.
class Bike(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    brand = models.CharField(max_length=100, null=True, blank=True)
    model = models.CharField(max_length=100, null=True, blank=True)
    year = models.IntegerField(null=True, blank=True)
    isFeatured = models.BooleanField(default=False)
    isAvailable = models.BooleanField(default=False)
    color = models.CharField(max_length=100, null=True, blank=True)
    start = models.CharField(max_length=100, choices=START_CHOICES, default='SELF_START_ONLY') 
    engine = models.CharField(max_length=100, null=True, blank=True) 
    distance = models.CharField(max_length=100, null=True, blank=True)  
    price = models.FloatField()
    description = models.TextField(null=True, blank=True)
    image = models.ImageField(upload_to='images/bikes', null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True)
    locations = models.ManyToManyField(Location, related_name="bikes")

    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='AVAILABLE')
    
    def __str__(self):
        return self.name
    def average_rating(self):
        # Calculate average rating for this bike
        avg_rating = self.ratings.aggregate(Avg('rating'))['rating__avg']
        return avg_rating if avg_rating is not None else 0.0

# Rating model

class Rating(models.Model):
    user= models.ForeignKey('authentication.User', on_delete=models.CASCADE)
    bike_id = models.ForeignKey(Bike, on_delete=models.CASCADE, related_name='ratings')
    rating = models.DecimalField(max_digits=3, decimal_places=1)
    comment = models.TextField(null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.bike_id.name} - {self.rating}"