from django.shortcuts import render
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.response import Response
from rest_framework import status
from .models import User
from rest_framework.views import APIView
import requests
from django.core.exceptions import ObjectDoesNotExist
from .serializers import pwAdminLoginSerializer
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
