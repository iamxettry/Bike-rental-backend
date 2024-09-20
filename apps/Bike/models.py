from django.db import models
import uuid


START_CHOICES = (
    ('SELF_START_ONLY', 'Self Start Only'),
    ('KICK_AND_SELF_START', 'Kick & Self Start'),
    ('KICK_START_ONLY', 'Kick Start Only'),
)


class Features(models.Model):
    start = models.CharField(max_length=100, choices=START_CHOICES, default='SELF START ONLY') 
    engine = models.CharField(max_length=100) 
    distance = models.CharField(max_length=100)  

    def __str__(self):
        return f"{self.engine}, {self.distance}, {self.start}"
# Create your models here.
class Bike(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    rating = models.DecimalField(max_digits=3, decimal_places=1)
    brand = models.CharField(max_length=100)
    model = models.CharField(max_length=100)
    year = models.IntegerField()
    color = models.CharField(max_length=100)
    features = models.OneToOneField(Features, on_delete=models.CASCADE)
    price = models.FloatField()
    description = models.TextField()
    image = models.ImageField(upload_to='images/bikes', null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name