# apps/blog/serializers.py

from rest_framework import serializers
from .models import Blog

class BlogSerializer(serializers.ModelSerializer):
    class Meta:
        model = Blog
        fields = ['id', 'title', 'description', 'image', 'author', 'created_at', 'updated_at']
        extra_kwargs = {
            'author': {'read_only': True},
        }