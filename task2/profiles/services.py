from django.conf import settings
from django.core.mail import send_mail


class GroupService:
    def __init__(self, user, value, mode):
        self.user = user
        self.value = value
        self.mode = mode

    def execute(self):
        self.change_user_rating()
        group = self.get_user_group(self.get_user_rating_count(self.user.rating))
        return self.set_user_group(group)

    def change_user_rating(self):
        if self.mode == 'up':
            self.user.rating += self.value
        if self.mode == 'down':
            self.user.rating -= self.value

    def get_user_group(self, count):
        user_groups = {
            '1': 'rank1',
            '2': 'rank2',
            '3': 'rank3',
            '4': 'rank4',
            '5': 'moderator'
        }
        return user_groups.get(str(count), 'usual_user')

    def get_user_rating_count(self, rating):
        result = rating // 100
        if result > 5:
            result = 5
        return result

    def send_email(self):
        url = settings.FRONTEND_HOST + '/?moderator_query=' + str(self.user.id)
        subject = '{} ({}) recommends you reading'.format(self.user.username, self.user.email)
        message = 'If you want to become moderator click the url {}'.format(url)
        send_mail(subject, message, 'admin@myblog.com', [self.user.email])

    def set_user_group(self, group):
        if self.user.user_group == 'moderator' and group == 'moderator':
            return self.user
        elif self.user.user_group != 'moderator' and group != 'moderator':
            self.user.user_group = group
        elif self.user.user_group != 'moderator' and group == 'moderator':
            self.send_email()
        return self.user


class UpdateUserProfileService:
    def __init__(self, user, serialized_data):
        self.user = user
        self.serialized_data = serialized_data

    def execute(self):
        return self.update_user_data()

    def update_user_data(self):
        if self.serialized_data['status']:
            self.user.status = self.serialized_data['status']
        if self.serialized_data['username']:
            self.user.username = self.serialized_data['username']
        if self.user.about_yourself and self.serialized_data['about_yourself']:
            self.user.about_yourself = self.serialized_data['about_yourself']
        elif self.serialized_data['about_yourself'] and not self.user.about_yourself:
            self.user = GroupService(self.user, 1, 'up').execute()
            self.user.about_yourself = self.serialized_data['about_yourself']
        if self.user.place_of_employment and self.serialized_data['place_of_employment']:
            self.user.place_of_employment = self.serialized_data['place_of_employment']
        elif self.serialized_data['place_of_employment'] and not self.user.place_of_employment:
            self.user = GroupService(self.user, 1, 'up').execute()
            self.user.place_of_employment = self.serialized_data['place_of_employment']
        if self.user.location and self.serialized_data['location']:
            self.user.location = self.serialized_data['location']
        elif self.serialized_data['location'] and not self.user.location:
            self.user = GroupService(self.user, 1, 'up').execute()
            self.user.location = self.serialized_data['location']
        return self.user
