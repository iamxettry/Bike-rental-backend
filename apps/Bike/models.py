from django.db import models
import uuid


START_CHOICES = (
            ('SELF', 'SELF START ONLY'),
            ('KICK_SELF', 'KICK & SELF START'),
            ('KICK', 'KICK START ONLY'),
        )
# Create your models here.
class Bike(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    brand = models.CharField(max_length=100)
    model = models.CharField(max_length=100)
    year = models.IntegerField()
    color = models.CharField(max_length=100)
    start = models.CharField(max_length=100, choices=START_CHOICES)
    price = models.FloatField()
    description = models.TextField()
    image = models.ImageField(upload_to='images/bikes', null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.brand + " " + self.model