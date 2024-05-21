from rest_framework import serializers
from .models import TagsCategory,Tag,TagsCategoryPermission

class TagsCategoryPermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = TagsCategoryPermission
        fields = ['id','name','created','modified']

class TagsCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = TagsCategory
        fields = ['id', 'name', 'role', 'created', 'modified']


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name', 'category', 'created', 'modified']