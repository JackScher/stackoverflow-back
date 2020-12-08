from django.db import transaction

from question.models import ModeratorStory


class ModeratorUpdateService:
    def __init__(self, instance, serialized_data, user, type_of_obj):
        self.instance = instance
        self.serialized_data = serialized_data
        self.user = user
        self.type_of_obj = type_of_obj

    @transaction.atomic
    def execute(self):
        old_data = self.get_data_list()
        self.update_instance()
        self.save_moderator_story(old_data)
        return self.instance

    def get_data_list(self):
        old_data = {
            'title': self.instance.title,
            'body': self.instance.body
        }
        return old_data

    def update_instance(self):
        if self.serialized_data['title']:
            self.instance.title = self.serialized_data['title']
        if self.serialized_data['body']:
            self.instance.body = self.serialized_data['body']
        self.instance.save()

    def save_moderator_story(self, old_data):
        new_data = self.get_data_list()
        ModeratorStory.objects.create(moderator=self.user, type=self.type_of_obj, object=self.instance.id,
                                      before_update=old_data, updated=new_data)
