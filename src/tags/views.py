from rest_framework import viewsets
from .models import TagsCategory, Tag
from .serializers import TagsCategorySerializer, TagSerializer
from app_auth.permissions import isAdminOrReadOnly
from rest_framework.permissions import IsAuthenticated
    

class TagsCategoryViewSet(viewsets.ModelViewSet):
    queryset = TagsCategory.objects.all()
    serializer_class = TagsCategorySerializer
    # permission_classes = [IsAuthenticated,isAdminOrReadOnly]
    http_method_names = ["get", "post", "delete", "head", "options", "trace"]
    def get_queryset(self):
        type = self.request.query_params.get('type')
        if type:
            return self.queryset.filter(type=type)
        return self.queryset.all()

class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    # permission_classes = [IsAuthenticated,isAdminOrReadOnly]
    http_method_names = ["get", "post", "delete", "head", "options", "trace"]

    def get_queryset(self):
        category_pk = self.request.query_params.get('category_pk')
        type = self.request.query_params.get('type')
        if category_pk:
            return self.queryset.filter(category_id=category_pk)
        elif type:
            return self.queryset.filter(category__type=type)
        else:
            return self.queryset.all()

