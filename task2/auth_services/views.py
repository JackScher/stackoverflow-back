from rest_auth.registration.views import SocialLoginView
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
import requests
import json
from auth_services.serializers import AuthSerializer
from profiles.models import UserProfile


class GoogleLogin(SocialLoginView):
    queryset = UserProfile.objects.all()
    serializer_class = AuthSerializer
    permission_classes = (AllowAny, )

    def post(self, request, *args, **kwargs):
        url = self.create_url(request)
        resp = requests.get(url)
        resp = json.loads(resp.text)
        result = self.logic(resp)
        result = AuthSerializer(result)
        return Response({'detail': result.data}, status=status.HTTP_200_OK)

    def create_url(self, request):
        url = 'https://www.googleapis.com/oauth2/v3/tokeninfo?id_token='
        id_token = request.data.get('id_token')
        url += id_token
        return url

    def logic(self, dict):
        user = self.check_user_exist(dict)
        if user:
            token = Token.objects.get(user=user)
            return {'key': token.key, 'user': user}
        else:
            curr_user = UserProfile.objects.create_user(email=dict['email'], username=dict['name'])
            curr_user.rating += 1
            curr_user.save()
            token = Token.objects.create(user=curr_user)
            return {'key': token.key, 'user': curr_user}


    def check_user_exist(self, dict):
        try:
            user = UserProfile.objects.get(email=dict['email'])
            return user
        except:
            return None


class LinkedinLogin(SocialLoginView):
    queryset = UserProfile.objects.all()
    serializer_class = AuthSerializer
    permission_classes = (AllowAny, )

    def post(self, request, *args, **kwargs):
        access_token = self.get_access_token(request)
        email = self.get_user_email(access_token)
        username = self.get_user_name(access_token)
        result = self.logic(email, username)
        result = AuthSerializer(result)
        return Response({'detail': result.data}, status=status.HTTP_200_OK)

    def get_access_token(self, request):
        url = 'https://www.linkedin.com/oauth/v2/accessToken?grant_type=authorization_code&redirect_uri=http%3A%2F%2Flocalhost%3A8080&client_id=78z5p6percm8do&client_secret=0iRzy06o3PN0fG0P&code=' + request.data['code']
        resp = requests.get(url)
        resp = json.loads(resp.text)
        return resp['access_token']

    def get_user_email(self, access_token):
        url = 'https://api.linkedin.com/v2/emailAddress?q=members&projection=(elements*(handle~))'
        headers = {'Authorization': 'Bearer ' + access_token}
        resp = requests.get(url, headers=headers)
        resp = json.loads(resp.text)
        return resp['elements'][0]['handle~']['emailAddress']

    def get_user_name(self, access_token):
        url = 'https://api.linkedin.com/v2/me'
        headers = {'Authorization': 'Bearer ' + access_token}
        resp = requests.get(url, headers=headers)
        resp = json.loads(resp.text)
        return resp['localizedFirstName']

    def logic(self, email, username):
        user = self.check_user_exist(email)
        if user:
            token = Token.objects.get(user=user)
            return {'key': token.key, 'user': user}
        else:
            curr_user = UserProfile.objects.create_user(email=email, username=username)
            curr_user.rating += 1
            curr_user.save()
            token = Token.objects.create(user=curr_user)
            return {'key': token.key, 'user': curr_user}

    def check_user_exist(self, email):
        try:
            user = UserProfile.objects.get(email=email)
            return user
        except:
            return None
