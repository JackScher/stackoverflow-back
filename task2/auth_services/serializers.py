from rest_framework import serializers
from rest_framework.authtoken.models import Token

from profiles.models import UserProfile


class UserIdSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['id']


class GoogleAuthSerializer(serializers.ModelSerializer):
    user = UserIdSerializer()

    class Meta:
        model = Token
        fields = ('key', 'user')
