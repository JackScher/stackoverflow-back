from profiles.models import UserProfile
from rest_framework.authtoken.models import Token


class AuthRegistrationService:
    def __init__(self, email, username):
        self.email = email
        self.username = username

    def execute(self):
        print(self.logic())
        return self.logic()

    def logic(self):
        user = self.check_user_exist()
        if user:
            token = Token.objects.get(user=user)
            return {'key': token.key, 'user': user}
        else:
            curr_user = UserProfile.objects.create_user(email=self.email, username=self.username)
            curr_user.rating += 1
            curr_user.save()
            token = Token.objects.create(user=curr_user)
            return {'key': token.key, 'user': curr_user}

    def check_user_exist(self):
        try:
            user = UserProfile.objects.get(email=self.email)
            return user
        except:
            return None