from djoser.serializers import UserCreatePasswordRetypeSerializer ,TokenCreateSerializer
from .models import User
class pwUserCreateSerializer(UserCreatePasswordRetypeSerializer):
    class Meta(UserCreatePasswordRetypeSerializer.Meta):
        model = User
        fields = ('id','email', 'username', 'password', 'first_name', 'last_name')
class pwAdminLoginSerializer(TokenCreateSerializer):
    class Meta:
        model = User
        fields = ('email','password')