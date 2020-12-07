from allauth.account.adapter import get_adapter
from django.contrib.auth import password_validation
from django.core.mail import send_mail
from django.db import models
from django.contrib.auth.models import AbstractUser

from django.conf import settings


class StatusChoice(models.TextChoices):
    status1 = 'none', 'none'
    status2 = 'educating', 'educating'
    status3 = 'working', 'working'


# class RankChoices(models.TextChoices):
#     rank1 = 'Freshman', 'Freshman'
#     rank2 = 'Middle', 'Middle'
#     rank3 = 'Experienced', 'Experienced'


class UserProfile(AbstractUser):
    status = models.CharField(max_length=9, choices=StatusChoice.choices, default=StatusChoice.status1)
    # rank = models.CharField(max_length=11, choices=RankChoices.choices, default=RankChoices.rank1)

    avatar = models.ImageField(null=True, blank=True)
    place_of_employment = models.CharField(max_length=255, null=True, blank=True)
    about_yourself = models.TextField(null=True, blank=True)
    location = models.CharField(max_length=255, null=True, blank=True)
    rating = models.IntegerField(default=10)
    user_group = models.CharField(max_length=255, default='usual_user')
