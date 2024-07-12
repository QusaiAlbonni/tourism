from djoser.serializers import UserCreatePasswordRetypeSerializer ,TokenCreateSerializer, UserSerializer as DjoserUserSerializer
from django.contrib.auth import get_user_model
from rest_framework.serializers import SerializerMethodField

User = get_user_model()

class pwUserCreateSerializer(UserCreatePasswordRetypeSerializer):
    class Meta(UserCreatePasswordRetypeSerializer.Meta):
        model = User
        fields = ('id','email', 'username', 'password', 'first_name', 'last_name')
class pwAdminLoginSerializer(TokenCreateSerializer):
    class Meta:
        model = User
        fields = ('email','password')

class UserSerializer(DjoserUserSerializer):
    permissions = SerializerMethodField()
    
    class Meta(DjoserUserSerializer.Meta):
        fields = DjoserUserSerializer.Meta.fields + ('permissions', )
    
    def get_permissions(self, instance):
        user_perms = instance.get_all_permissions()
        permissions_codenames = [perm.split('.')[1] for perm in user_perms]
        
        return permissions_codenames