from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import TagsCategory,Tag,TagsCategoryPermission
from .serializers import TagsCategorySerializer,TagSerializer,TagsCategoryPermissionSerializer
from django.apps import apps
from app_auth.permissions import isAdminOrReadOnly
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly

class TagsCategoryPermissionViewSet(viewsets.ModelViewSet):
    queryset = TagsCategoryPermission.objects.all()
    serializer_class = TagsCategoryPermissionSerializer
    permission_classes = [IsAuthenticated, isAdminOrReadOnly]

    def create(self, request, *args, **kwargs):
        name = request.data.get('name')
        models = apps.get_models()
        models_with_tag = [model for model in models if 'tag' in [field.name for field in model._meta.fields]]
        model_names = [model.__name__ for model in models_with_tag]
        available_model_names = [name for name in model_names if name not in [perm.name.lower() for perm in TagsCategoryPermission.objects.all()]]
        if(name not in available_model_names):
            return Response({'massege':'cant','tags_permission_can_from': available_model_names}, status=status.HTTP_400_BAD_REQUEST)
        return super().create(request, *args, **kwargs)
    
    @action(detail=False, methods=['get'])
    def show_models(self, request, *args, **kwargs):
        models = apps.get_models()
        models_with_tag = [model for model in models if 'tag' in [field.name for field in model._meta.fields]]
        model_names = [model.__name__ for model in models_with_tag]
        available_model_names = [name for name in model_names if name not in [perm.name.lower() for perm in TagsCategoryPermission.objects.all()]]
        return Response({'tags_permission_can_from': available_model_names}, status=status.HTTP_200_OK)
    

class TagsCategoryViewSet(viewsets.ModelViewSet):
    queryset = TagsCategory.objects.all()
    serializer_class = TagsCategorySerializer


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer

