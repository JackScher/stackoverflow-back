from django.contrib import admin

from question.models import Question, Answer, Skill, Tag, Comment, Vote, ModeratorStory

admin.site.register(Question)
admin.site.register(Answer)
admin.site.register(Vote)

admin.site.register(Tag)
admin.site.register(Skill)
admin.site.register(Comment)

admin.site.register(ModeratorStory)
