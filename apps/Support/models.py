from django.db import models
from django.utils.timezone import now
from uuid import uuid4

# FAQ Model
class FAQ(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
    ]
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    question = models.TextField()
    answer = models.TextField()
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='draft')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.question

# Customer Support Model
class CustomerSupport(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    address = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.email

# Report Issue Model
class ReportIssue(models.Model):
    CATEGORY_CHOICES = [
        ('technical', 'Technical'),
        ('billing', 'Billing'),
        ('feedback', 'Feedback'),
        ('other', 'Other'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    subject = models.CharField(max_length=255)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.subject

# System Alert Model
class SystemAlert(models.Model):
    STATUS_CHOICES = [
        ('critical', 'Critical'),
        ('resolved', 'Resolved'),
        ('upcoming', 'Upcoming'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    title = models.CharField(max_length=255)
    description = models.TextField()
    date_time = models.DateTimeField(default=now)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES)

    def __str__(self):
        return self.title
