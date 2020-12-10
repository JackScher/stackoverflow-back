from allauth.account.views import ConfirmEmailView
from django_filters.rest_framework import DjangoFilterBackend

# from rest_auth.models import TokenModel
# from rest_auth.registration.app_settings import RegisterSerializer, register_permission_classes

from rest_auth.models import TokenModel
from rest_auth.registration.app_settings import register_permission_classes, RegisterSerializer
from rest_auth.registration.views import RegisterView
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from profiles.models import UserProfile
from profiles.serializers import UserProfileSerializer, UpdateUserProfileSerializer
from profiles.services import UpdateUserProfileService, GroupService
from task2 import settings


class CustomView(APIView, ConfirmEmailView):
    permission_classes = (AllowAny,)
    allowed_methods = ('POST', 'OPTIONS', 'HEAD')

    def post(self, request, key, *args, **kwargs):
        confirmation = self.get_object()
        confirmation.confirm(key)
        return Response({'detail': ('ok')}, status=status.HTTP_200_OK)


class ProfileView(ModelViewSet):
    queryset = UserProfile.objects.all()
    permission_classes = (IsAuthenticatedOrReadOnly,)
    filter_backends = [DjangoFilterBackend]
    filter_fields = ['id']
    serializer_class = UserProfileSerializer


class RegisterUserProfileView(RegisterView):
    serializer_class = RegisterSerializer
    permission_classes = register_permission_classes()
    token_model = TokenModel

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = self.perform_create(serializer)

        user_status = request.data.get("status")
        place_of_employment = request.data.get("place_of_employment")
        about_yourself = request.data.get("about_yourself")
        location = request.data.get("location")

        if user_status:
            user.status = user_status
        if place_of_employment:
            user.place_of_employment = place_of_employment
        if about_yourself:
            user.about_yourself = about_yourself
        if location:
            user.location = location

        self.add_rating(user)

        headers = self.get_success_headers(serializer.data)

        return Response(self.get_response_data(user),
                        status=status.HTTP_201_CREATED,
                        headers=headers)

    def mapping_for_rating(self, user, field):
        rating_mapping = {
            'status': user.status,
            'place_of_employment': user.place_of_employment,
            'about_yourself': user.about_yourself,
            'location': user.location
        }
        if field:
            return rating_mapping.get(field, None)
        return None

    def add_rating(self, user):
        keys = user.__dict__.keys()
        for key in keys:
            res = self.mapping_for_rating(user, key)
            if res:
                user.rating += 1
        user.save()


class UpdateUserProfileView(ModelViewSet):
    queryset = UserProfile.objects.all()
    permission_classes = (IsAuthenticatedOrReadOnly, )
    serializer_class = UpdateUserProfileSerializer

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        changed_user = UpdateUserProfileService(request.user, serializer.validated_data).execute()
        serialized_data = UpdateUserProfileSerializer(changed_user)
        return Response({'detail': serialized_data.data}, status=status.HTTP_200_OK)


class ConfirmModeratorViewSet(ModelViewSet):
    queryset = UserProfile.objects.all()
    permission_classes = (AllowAny, )
    lookup_field = 'id'
    serializer_class = UserProfileSerializer

    def put(self, request, *args, **kwargs):
        return self.update(request, id=None, *args, **kwargs)

    def update(self, request, id=None, *args, **kwargs):
        try:
            user = UserProfile.objects.get(id=int(id))
        except:
            return Response({'detail': 'user is not exist'}, status=status.HTTP_200_OK)
        if GroupService(user, None, None).get_user_group(GroupService(user, None, None).get_user_rating_count(user.rating)) == 'moderator':
            user.user_group = 'moderator'
            user.save()
        serialized_data = UserProfileSerializer(user)
        return Response({'detail': serialized_data.data}, status=status.HTTP_200_OK)
