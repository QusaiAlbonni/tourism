from rest_framework import serializers
from .models import Guide

class GuideSerializer(serializers.ModelSerializer):
    class Meta:
        model = Guide
        fields = [
            'name',
            'bio',
            'avatar',
            'likes',
            'email'
        ]
        read_only_fields = ('likes',)