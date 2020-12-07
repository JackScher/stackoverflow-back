from datetime import datetime
from question.models import ModeratorStory


class ModeratorUpdateService:
    def __init__(self, instance, serialized_data, user, type):
        self.instance = instance
        self.serialized_data = serialized_data
        self.user = user
        self.type = type

    def execute(self):
        pass

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

    def save_moderator_story(self, old_data, new_data):
        ModeratorStory.objects.create(moderator=self.user, type=self.type, object=self.instance.id, date=datetime.now(),
                                      before_update=old_data, updated=new_data)
