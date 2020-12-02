from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.db import models
from mptt.fields import TreeForeignKey
from mptt.models import MPTTModel


class DateParent(models.Model):
    date_create = models.DateTimeField(auto_now_add=True)                           #, format=settings.REST_FRAMEWORK['DATETIME_FORMAT']
    date_update = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Comment(MPTTModel, DateParent):
    text = models.TextField()
    user_id = models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True)

    # level = models.CharField(max_length=255, default='')
    # lft = models.CharField(max_length=255, default='')
    # rght = models.CharField(max_length=255, default='')
    # tree_id = models.IntegerField(default=1)

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, related_name='comments')
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')

    class MPTTMeta:
        order_insertion_by = ['text']


class Question(DateParent):
    title = models.CharField(max_length=255)
    body = models.TextField()
    user_id = models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='questions')
    comments = GenericRelation(Comment)


class Answer(DateParent):
    title = models.CharField(max_length=255)
    body = models.TextField()
    user_id = models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='answers')
    question_id = models.ForeignKey(to=Question, on_delete=models.CASCADE, related_name='answers')

    comments = GenericRelation(Comment)


class Tag(DateParent):
    name = models.CharField(max_length=255)
    question_id = models.ManyToManyField(to=Question, related_name='tags', blank=True)


class Skill(models.Model):
    user_id = models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    tag_id = models.ManyToManyField(to=Tag)


class Vote(DateParent):
    voter = models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='voter', default=1)
    action = models.CharField(max_length=255, default='up')

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, related_name='vote')
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')


class ModeratorStory(models.Model):
    moderator = models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    type = models.CharField(max_length=255)
    object = models.IntegerField()
    date = models.DateTimeField()
    before_update = models.CharField(max_length=255, blank=True)
    updated = models.CharField(max_length=255, blank=True)
