from rest_framework import viewsets
from .models import TagsCategory, Tag
from .serializers import TagsCategorySerializer, TagSerializer
from app_auth.permissions import isAdminOrReadOnly
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response

class TagsCategoryViewSet(viewsets.ModelViewSet):
    queryset = TagsCategory.objects.all()
    serializer_class = TagsCategorySerializer
    permission_classes = [IsAuthenticated,isAdminOrReadOnly]
    http_method_names = ["get", "post", "delete", "head", "options", "trace"]
    def get_queryset(self):
        type = self.request.query_params.get('type')
        if type:
            return self.queryset.filter(type=type)
        return self.queryset.all()
    
    @action(detail=False, methods=['get'], url_path='by-type')
    def get_categories_with_tags(self, request):
        category_type = request.query_params.get('type')
        if not category_type:
            return Response({"error": "Type parameter is required."}, status=400)

        categories = TagsCategory.objects.filter(type=category_type)
        response_data = []

        for category in categories:
            tags = Tag.objects.filter(category=category)
            tags_serializer = TagSerializer(tags, many=True)
            response_data.append({
                "category": TagsCategorySerializer(category).data,
                "tags": tags_serializer.data
            })

        return Response(response_data)
    

class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [IsAuthenticated,isAdminOrReadOnly]
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

