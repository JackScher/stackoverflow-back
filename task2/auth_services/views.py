from rest_auth.registration.views import SocialLoginView
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
import requests
import json
from auth_services.serializers import GoogleAuthSerializer
from profiles.models import UserProfile


class GoogleLogin(SocialLoginView):
    queryset = UserProfile.objects.all()
    serializer_class = GoogleAuthSerializer
    permission_classes = (AllowAny, )

    def post(self, request, *args, **kwargs):
        url = self.create_url(request)
        resp = requests.get(url)
        resp = json.loads(resp.text)
        result = self.logic(resp)
        result = GoogleAuthSerializer(result)
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
