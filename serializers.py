from django.contrib.auth import get_user_model
from rest_framework import serializers
from .models import File

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'ops_user')

class FileSerializer(serializers.ModelSerializer):
    class Meta:
        model = File
        fields = '__all__'

