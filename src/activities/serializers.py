from rest_framework import serializers
from .models import Guide




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
            'liked',
            'is_popular'
        ]
        read_only_fields = ('likes', 'liked')
    def get_liked(self, obj : Guide) -> bool:
        user = self.context['request'].user
        if user.is_authenticated:
            return obj.is_liked_by_user(user)
        return False