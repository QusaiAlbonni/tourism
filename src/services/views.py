
from django.db import models
from rest_framework.response import Response
from rest_framework import status
from .models import Service
from .exceptions  import AdmincantFav,serviceCantReview,AdmincantReview
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from app_auth.permissions import isAdminOrReadOnly
from rest_framework.decorators import action
from rest_framework import viewsets, permissions
from .models import ServiceFavorite
from .serializers import ServiceFavoriteSerializer
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import PermissionDenied
from django.db.models import Case, When, Value, IntegerField ,F
from rest_framework import viewsets, permissions
from .models import ServiceReview
from .serializers import ServiceReviewSerializer
from .models import ServiceDiscount
from .serializers import ServiceDiscountSerializer
from rest_framework import viewsets
from .models import ServicePhoto
from .serializers import ServicePhotoSerializer
from django.core.exceptions import ValidationError
from rest_framework.exceptions import NotFound
from .utils import get_reviews_prompt
from gemini.services import GeminiGenerateContent
from django.utils.translation import get_language
from django.utils.translation import gettext_lazy as _
from django.http import Http404

class ServicePhotoViewSet(viewsets.ModelViewSet):
    queryset = ServicePhoto.objects.all()
    permission_classes = [isAdminOrReadOnly]
    serializer_class = ServicePhotoSerializer
    
    def get_queryset(self):
        service_pk = self.request.query_params.get('service_pk')
        if service_pk:
            return self.queryset.filter(service_id=service_pk)
        return self.queryset.all()
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        try:
            self.perform_destroy(instance)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except ValidationError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

class ServiceFavoriteViewSet(viewsets.ModelViewSet):
    serializer_class = ServiceFavoriteSerializer
    permission_classes = [IsAuthenticated]
    queryset = ServiceFavorite.objects.all()

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.custom_get_queryset(request, *args, **kwargs))

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    def custom_get_queryset(self,request,*args, **kwargs):
        user = request.query_params.get('user_id', None)
        service = request.query_params.get('service_id', None)
        if self.request.user.is_admin:
            if user and service:
                return self.queryset.filter(user=user,service=service)
            elif user:
                return self.queryset.filter(user=user)
            elif service:
                return self.queryset.filter(service=service)
            else:
                return self.queryset.all()
        return self.queryset.filter(user=self.request.user)
    
    def create(self, request, *args, **kwargs):
        user = request.user
        if user.is_admin:
            raise AdmincantFav()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    
    def update(self, request, *args, **kwargs):
        raise PermissionDenied("Updating favorites is not allowed.")

    def partial_update(self, request, *args, **kwargs):
        raise PermissionDenied("Updating favorites is not allowed.")
    
    def destroy(self, request, *args, **kwargs):
        user = request.user
        service = kwargs.get('pk')
        if user.is_admin:
            raise AdmincantFav()
        instance=get_object_or_404(self.queryset, user=user, service=service)
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)
        
class ServiceReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ServiceReviewSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    queryset = ServiceReview.objects.all()  
    
    def list(self, request, *args, **kwargs):

        queryset = self.filter_queryset(self.custom_get_queryset(request, *args, **kwargs))
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            if (not self.request.user.is_anonymous) and self.request.user.is_admin:
                return self.get_paginated_response(serializer.data)
            else:
                reviews = serializer.data
                for review in reviews:
                    if review['user'] == request.user.id:
                        review['can_delete'] = 1
                    else:
                        review['can_delete'] = 0
                response_data ={
                'reviews':reviews,
                'user_can_review':1 if not queryset.filter(user_id=self.request.user.id).exists() else 0
                }

                return self.get_paginated_response(response_data)
        
        serializer = self.get_serializer(queryset, many=True)

        if self.request.user.is_admin:
            return Response(serializer.data)
        else:
            response_data ={
                'reviews':serializer.data,
                'user_can_review':1 if not queryset.filter(user=self.request.user).exists() else 0
            }
        return Response(response_data)

    def custom_get_queryset(self,request,*args, **kwargs):
        user = request.query_params.get('user_id', None)
        service = request.query_params.get('service_id', None)
        get_object_or_404(Service, pk = service)
        if (not self.request.user.is_anonymous) and self.request.user.is_admin:
            if user and service:
                return self.queryset.filter(user=user,service=service)
            elif user:
                return self.queryset.filter(user=user)
            elif service:
                return self.queryset.filter(service=service)
            else:
                return self.queryset.all()
        
        query = self.queryset.filter(service=service)
        ordered_query = query.order_by(
            Case(
                When(user=self.request.user, then=Value(-1)),  
                default=Value(1)           
            )
        )

        return ordered_query

    def create(self, request, *args, **kwargs):
        user = request.user
        if user.is_admin:
            raise AdmincantFav()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    
    def update(self, request, *args, **kwargs):
        raise PermissionDenied("Updating favorites is not allowed.")

    def partial_update(self, request, *args, **kwargs):
        raise PermissionDenied("Updating favorites is not allowed.")
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.user != request.user:
            return Response({"detail": "You do not have permission to delete this review."}, status=status.HTTP_403_FORBIDDEN)
        try:
            instance.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except ValidationError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(methods=["get"], detail=False, permission_classes= [IsAuthenticated])
    def me(self, request, *args, **kwargs):
        service_id = request.query_params.get('service_id', None)
        user = request.user
        if user.is_admin:
            raise AdmincantFav()
        try:
            review = ServiceReview.objects.get(service=service_id, user=user)
        except ServiceReview.DoesNotExist:
            raise NotFound("No review found for the specified service by the user.")
        serializer = self.get_serializer(review)
        return Response(serializer.data)
    
    @action(methods=["get"], detail=False)
    def summary(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.custom_get_queryset(request))
        service_id = request.query_params.get('service_id', None)
        if service_id is None:
            raise Http404()
        service = Service.objects.get(pk = service_id)
        lang = get_language()
        if lang not in GeminiGenerateContent.locales:
            lang = 'en'
        prompt_dict = get_reviews_prompt(queryset, language=lang, service= service)
        try:
            result = GeminiGenerateContent.execute(inputs =prompt_dict)
        except Exception as e:
            return Response({'detail': str(e)}, status.HTTP_503_SERVICE_UNAVAILABLE)
            
        return Response({'result': result}, status.HTTP_200_OK)
        

class ServiceDiscountViewSet(viewsets.ModelViewSet):
    queryset = ServiceDiscount.objects.all()
    permission_classes = [isAdminOrReadOnly]
    serializer_class = ServiceDiscountSerializer

    def get_queryset(self):
       service_pk = self.request.query_params.get('service_pk')
       
       if service_pk:
           return self.queryset.filter(service_id=service_pk)
       return self.queryset.all()