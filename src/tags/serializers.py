from rest_framework import serializers
from .models import TagsCategory, Tag

class TagsCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = TagsCategory
        fields = ['id', 'name', 'type', 'created', 'modified']

class TagSerializer(serializers.ModelSerializer):
    # category = TagsCategorySerializer()
    class Meta:
        model = Tag
        fields = ['id', 'name', 'contenttype', 'category', 'created', 'modified']
