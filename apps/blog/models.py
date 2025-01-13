# apps/blog/models.py

from django.db import models
from apps.auth.models import User
import uuid
from tinymce.models import HTMLField


class Blog(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    description = HTMLField()
    image = models.ImageField(upload_to='blogs/', null=True, blank=True)
    author = models.ForeignKey(User, related_name='blogs', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
