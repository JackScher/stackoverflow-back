from rest_framework.routers import DefaultRouter

from question.views import QuestionViewSet, AnswerCreateView, CommentCreateViewSet, TagViewSet, SkillViewSet, \
    QuestionItemViewSet, QuestionCreateView, VoteViewSet, AddTagRelationViewSet, RemoveTagRelation, TagDeleteViewSet, \
    ModeratorQuestionEditViewSet, ModeratorAnswerEditViewSet, AnswerListViewSet, SkillUpdateViewSet, \
    QuestionUpdateViewSet, AnswerUpdateViewSet, CommentUpdateViewSet, SkillRemoveTagRelation, SkillDeleteViewSet

router = DefaultRouter()
router.register('api/answers', AnswerListViewSet)
router.register('api/answer/create', AnswerCreateView)
router.register('api/answer/edit', AnswerUpdateViewSet)

router.register('api/vote', VoteViewSet)
router.register('api/questions', QuestionViewSet)
router.register('api/question/edit', QuestionUpdateViewSet)
router.register('api/question/item', QuestionItemViewSet)
router.register('api/question/create', QuestionCreateView)
router.register('api/moderator/question/edit', ModeratorQuestionEditViewSet)
router.register('api/moderator/answer/edit', ModeratorAnswerEditViewSet)

router.register('api/comment/create', CommentCreateViewSet)
router.register('api/comment/edit', CommentUpdateViewSet)

router.register('api/tags', TagViewSet)
router.register('api/tag/update', AddTagRelationViewSet)
router.register('api/tag/delete', TagDeleteViewSet)
router.register('api/tag/remove', RemoveTagRelation)

router.register('api/skills', SkillViewSet)
# router.register('api/skills/create', SkillCreateViewSet)
router.register('api/skills/delete', SkillDeleteViewSet)
router.register('api/skills/delete_tag', SkillRemoveTagRelation)
router.register('api/skills/update', SkillUpdateViewSet)

# router.register('api/check', Check)
# router.register('api/check/v2', Check_v2)

# router.register('api/check', Check)
# router.register('api/sheck', Check_v2)

urlpatterns = [
    # path('test', View.as_view())
]
urlpatterns += router.urls
