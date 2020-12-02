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


class RankChoices(models.TextChoices):
    rank1 = 'Freshman', 'Freshman'
    rank2 = 'Middle', 'Middle'
    rank3 = 'Experienced', 'Experienced'


class UserProfile(AbstractUser):
    status = models.CharField(max_length=9, choices=StatusChoice.choices, default=StatusChoice.status1)
    rank = models.CharField(max_length=11, choices=RankChoices.choices, default=RankChoices.rank1)

    avatar = models.ImageField(null=True, blank=True)
    place_of_employment = models.CharField(max_length=255, null=True, blank=True)
    about_yourself = models.TextField(null=True, blank=True)
    location = models.CharField(max_length=255, null=True, blank=True)
    rating = models.IntegerField(default=10)
    user_group = models.CharField(max_length=255, default='usual_user')

    def save(self, *args, **kwargs):

        self.check_group()

        super().save(*args, **kwargs)
        if self._password is not None:
            password_validation.password_changed(self._password, self)
            self._password = None

    def check_group(self):
        if self.rating > 500:
            message = self.check_is_moderator()
            if message:
                return message
            else:
                self.send_email()
        if self.rating > 400:
            self.user_group = 'rank4'
            return True
        if self.rating > 300:
            self.user_group = 'rank3'
            return True
        if self.rating > 200:
            self.user_group = 'rank2'
            return True
        if self.rating > 100:
            self.user_group = 'rank1'
            return True

    def send_email(self):
        url = self.create_link()
        subject = '{} ({}) recommends you reading'.format(self.username, self.email)
        message = 'If you want to become moderator click the url {}'.format(url)
        send_mail(subject, message, 'admin@myblog.com', [self.email])

    def create_link(self):
        url = settings.FRONTEND_HOST + '/?moderator_query=' + str(self.id)
        return url

    def check_is_moderator(self):
        if self.user_group == 'moderator':
            return 'already moderator'
