from djoser.serializers import UserCreatePasswordRetypeSerializer
from .models import User
from djoser.serializers import UserCreateSerializer
class pwUserCreateSerializer(UserCreatePasswordRetypeSerializer):
    class Meta(UserCreatePasswordRetypeSerializer.Meta):
        model = User
        fields = ('id','email', 'username', 'password', 'first_name', 'last_name')
class pwAdminLoginSerializer(UserCreateSerializer):
    class Meta(UserCreateSerializer.Meta):
        model = User
        fields = ('email','password')
        