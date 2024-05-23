from rest_framework import serializers
from .models import Guide

from .models import ActivityTag

class ActivityTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = ActivityTag
        fields = ('id', 'tag', 'name', 'created', 'modified')


class GuideSerializer(serializers.ModelSerializer):
    liked = serializers.SerializerMethodField()
    class Meta:
        model = Guide
        fields = [
            'name',
            'bio',
            'avatar',
            'likes',
            'email',
            'liked'
        ]
        read_only_fields = ('likes', 'liked')
    def get_liked(self, obj : Guide) -> bool:
        user = self.context['request'].user
        if user.is_authenticated:
            return obj.is_liked_by_user(user)
        return False