from djoser.serializers import UserCreatePasswordRetypeSerializer ,TokenCreateSerializer
from django.contrib.auth import get_user_model

User = get_user_model()

class pwUserCreateSerializer(UserCreatePasswordRetypeSerializer):
    class Meta(UserCreatePasswordRetypeSerializer.Meta):
        model = User
        fields = ('id','email', 'username', 'password', 'first_name', 'last_name')
class pwAdminLoginSerializer(TokenCreateSerializer):
    class Meta:
        model = User
        fields = ('email','password')