from allauth.account.adapter import get_adapter
from allauth.account.utils import setup_user_email
from rest_auth.registration.serializers import RegisterSerializer
from rest_framework import serializers
from rest_framework.authtoken.models import Token
from rest_framework.serializers import SerializerMetaclass

from profiles.models import UserProfile
from question.models import Answer, Question


class AnswerModuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = ['id', 'title', 'body', 'user_id']


class QuestionsModuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ['id', 'title', 'body', 'user_id']


class UserProfileSerializer(serializers.ModelSerializer):
    answers = AnswerModuleSerializer(many=True)
    questions = QuestionsModuleSerializer(many=True)

    class Meta:
        model = UserProfile
        fields = ['id', 'username', 'password', 'email', 'avatar', 'place_of_employment', 'about_yourself', 'location',
                  'rank', 'status', 'answers', 'questions', 'rating', 'user_group']


class UserIdSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['id', 'user_group']


class MyCustomTokenSerializer(serializers.ModelSerializer):
    user = UserIdSerializer()

    class Meta:
        model = Token
        # fields = ('key', 'user', 'username', 'password', 'email', 'avatar', 'place_of_employment', 'about_yourself', 'location',
        #           'status', 'rank')
        fields = ('key', 'user')


class UpdateUserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['id', 'username', 'password', 'email', 'avatar', 'place_of_employment', 'about_yourself', 'location',
                  'status', 'rank']
