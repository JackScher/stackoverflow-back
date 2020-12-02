import requests
from allauth.account.models import EmailConfirmationHMAC, EmailConfirmation
from allauth.account.views import LoginView, ConfirmEmailView, SignupView
# from allauth.socialaccount.views import SignupView
from django.conf import settings
from django.http import Http404
from django.shortcuts import render
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView


from profiles.models import UserProfile


# class CustomLoginView(APIView, LoginView, SignupView):
#     permission_classes = (AllowAny,)
#     allowed_methods = ('POST', 'OPTIONS', 'HEAD')
#
#     def post(self, request, key):
#         print('KEY: ', key)
#         users = UserProfile.objects.all()
#         user = self.get_object(users, key)
#         if user:
#             user.login(key)
#             return Response({'detail': ('ok')}, status=status.HTTP_200_OK)
#         else:
#             UserProfile.objects.create_user({
#                 'username': user['username'],
#                 'password': user['password'],
#                 'email': user['email'],
#             })
#             return Response({'detail': ('ok')}, status=status.HTTP_200_OK)
#
#     def get_object(self, queryset=None, key):
#         # key = self.kwargs["access_key"]
#         emailconfirmation = EmailConfirmationHMAC.from_key(key)
#         if not emailconfirmation:
#             if queryset is None:
#                 queryset = self.get_queryset()
#             try:
#                 emailconfirmation = queryset.get(key=key.lower())
#             except EmailConfirmation.DoesNotExist:
#                 raise Http404()
#         return emailconfirmation


class CustomGoogleAuthView(APIView):
    permission_classes = (AllowAny,)
    allowed_methods = ('POST')

    def post(self, request, key):
        result = requests.get('https://openidconnect.googleapis.com/v1/userinfo',
                              params={
                                  # 'WWW - Authenticate: Basic realm': "api",
                                  'access_token': key,
                                  'alt': 'json'
                              })
        print(result)
        return Response({'detail': result}, status=status.HTTP_200_OK)


        # current_user = UserProfile.objects.filter(access_token=key)
        # if current_user:
        #     return Response({'detail': ('ok')}, status=status.HTTP_200_OK)
        # else:
        #     new_user = UserProfile.objects.create_user(username=request.username, password=request.password,
        #                                                email=request.email, access_token=key)
        #     Token.objects.create(user=new_user)
        #     return Response({'detail': ('ok')}, status=status.HTTP_200_OK)

    #need meth to get all user data using his google-token.
    #check google.oauth2.service_account.Credentials,  register_by_access_token

    # def get_user_info(self, request):
    #     result = requests.get('https://openidconnect.googleapis.com/v1/userinfo',
    #                  params={
    #                      'access_token': request.data.get('access_token'),
    #                      'alt': 'json'
    #                  })
    #     print(result)
