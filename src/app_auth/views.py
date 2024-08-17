from django.conf import settings
from django.shortcuts import render
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import viewsets
from .models import User
from rest_framework.views import APIView
import requests
from .serializers import pwAdminLoginSerializer
from djoser.views import UserViewSet as DjoserUserViewSet


class WebLoginView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        serializer = pwAdminLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = User.objects.get(email=request.data['email'])
        if user.is_admin:
            return super().post(request, *args, **kwargs)
        else:
            return Response({'error': 'Unauthorized access'}, status=status.HTTP_401_UNAUTHORIZED)

class UserActivationView(APIView):
    def get(self, request, uid, token):
        protocol = 'https://' if request.is_secure() else 'http://'
        web_url = protocol + request.get_host()
        post_url = web_url + "/auth/users/activation/"
        post_data = {'uid': uid, 'token': token}
        result = requests.post(post_url, data=post_data)
        content = result.text
        return Response(content)
    
class UserResetPasswordView(APIView):
    def get(self,request,uid,token):
        return render(request, 'reset_password.html')
    
    def post(self, request, uid, token):  
        new_password = request.POST.get('new_password')
        re_new_password = request.POST.get('re_new_password')

        if new_password != re_new_password:
            context = {'error_message': 'Passwords do not match'}
            return render(request, 'reset_password.html', context)

        protocol = 'https://' if request.is_secure() else 'http://'
        web_url = protocol + request.get_host()
        post_url = web_url + "/auth/users/reset_password_confirm/"

        data = {
            'uid': uid,
            'token': token,
            'new_password': new_password,
            're_new_password': re_new_password
        }

        response = requests.post(post_url, data=data)
        
        if response.status_code == 204:  # Assuming 200 indicates success
             return render(request, 'reset_good.html')

        context = {'error_message': 'Password reset failed'}
        return render(request, 'reset_password.html', context)
    
class UserViewSet(DjoserUserViewSet):
    def get_queryset(self):
        user = self.request.user
        queryset = viewsets.ModelViewSet.get_queryset(self)
        if settings.DJOSER.get('HIDE_USERS', True) and self.action == "list" and not (user.is_staff or user.is_admin):
            queryset = queryset.filter(pk=user.pk)
        return queryset
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)

        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)