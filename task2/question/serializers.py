from rest_framework import serializers
from rest_framework.fields import Field

from profiles.models import UserProfile
from question.models import Question, Answer, Comment, Tag, Skill, Vote


class TagModuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name']


class UserProfileModuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['id', 'username']


# class CommentCommentModuleSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Comment
#         fields = ['id', 'text', 'content_type', 'object_id', 'user_id']


class CommentModuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['id', 'text', 'object_id', 'user_id']


class QuestionSerializer(serializers.ModelSerializer):
    tags = TagModuleSerializer(many=True)
    user_id = UserProfileModuleSerializer()
    comments = CommentModuleSerializer(many=True)

    class Meta:
        model = Question
        fields = ['id', 'title', 'body', 'date_create', 'date_update', 'user_id', 'tags', 'comments']


class QuestionCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ['id', 'title', 'body', 'user_id']


class AnswerModuleSerializer(serializers.ModelSerializer):
    user_id = UserProfileModuleSerializer()
    comments = CommentModuleSerializer(many=True)

    class Meta:
        model = Answer
        fields = ['id', 'title', 'body', 'user_id', 'comments']


class QuestionItemSerializer(serializers.ModelSerializer):
    answers = AnswerModuleSerializer(many=True)
    tags = TagModuleSerializer(many=True)
    comments = CommentModuleSerializer(many=True)
    user_id = UserProfileModuleSerializer()

    class Meta:
        model = Question
        fields = ['id', 'title', 'body', 'answers', 'tags', 'comments', 'user_id']


class AnswerCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = ['id', 'title', 'body', 'date_create', 'date_update', 'user_id', 'question_id']


class CommentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['id', 'text', 'content_type', 'object_id', 'user_id']


class VoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vote
        fields = ['id', 'voter', 'action', 'date_create', 'date_update', 'content_type', 'object_id']


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'question_id')


class TagUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'question_id')


class TagDeleteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'question_id')


class RemoveTagRelationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'question_id')


class ModeratorQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ('id', 'title', 'body', 'user_id')


class ModeratorAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = ('id', 'title', 'body', 'user_id')


class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = '__all__'
