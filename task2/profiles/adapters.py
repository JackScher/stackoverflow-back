from allauth.account.adapter import DefaultAccountAdapter
from allauth.account.utils import user_email, user_username, user_field
from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site

from profiles.models import UserProfile


class CustomAdapter(DefaultAccountAdapter):
    def get_email_confirmation_url(self, request, emailconfirmation):
        """Constructs the email confirmation (activation) url.

        Note that if you have architected your system such that email
        confirmations are sent outside of the request context `request`
        can be `None` here.
        """
        url = settings.FRONTEND_HOST + '/?URLquery=' + emailconfirmation.key
        return url
