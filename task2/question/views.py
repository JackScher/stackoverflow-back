from datetime import datetime, timedelta
# import datetime
from django.db import transaction
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.permissions import IsAuthenticatedOrReadOnly, AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from profiles.models import UserProfile
from profiles.services import GroupService
from question.models import Question, Answer, Comment, Tag, Skill, Vote, ModeratorStory
from question.permissions import IsModerator, IsOwner
from question.serializers import QuestionSerializer, TagSerializer, \
    SkillSerializer, QuestionItemSerializer, QuestionCreateSerializer, AnswerCreateSerializer, CommentCreateSerializer, \
    VoteSerializer, TagUpdateSerializer, RemoveTagRelationSerializer, TagDeleteSerializer, ModeratorQuestionSerializer, \
    ModeratorAnswerSerializer, AnswerModuleSerializer, SkillRemoveTagRelationSerializer
from question.services import ModeratorUpdateService


########################################################################################################################


class QuestionViewSet(ModelViewSet):
    queryset = Question.objects.all()
    permission_classes = (IsAuthenticatedOrReadOnly, )
    serializer_class = QuestionSerializer


class QuestionUpdateViewSet(ModelViewSet):
    queryset = Question.objects.all()
    permission_classes = (IsAuthenticatedOrReadOnly, IsOwner)
    serializer_class = QuestionSerializer

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        question = Question.objects.get(id=request.data['id'])
        title = request.data.get('title')
        body = request.data.get('body')
        if title:
            question.title = title
        if body:
            question.body = body
        question.save()
        return Response({'detail': ('ok')}, status=status.HTTP_200_OK)


class QuestionItemViewSet(ModelViewSet):
    queryset = Question.objects.all()
    permission_classes = (IsAuthenticatedOrReadOnly, )
    filter_backends = [DjangoFilterBackend]
    filter_fields = ['id']
    serializer_class = QuestionItemSerializer


class QuestionCreateView(ModelViewSet):
    queryset = Question.objects.all()
    permission_classes = (IsAuthenticatedOrReadOnly, )
    serializer_class = QuestionCreateSerializer

    def create(self, request, *args, **kwargs):
        check = self.check(request.user)
        if check:
            return Response({'detail': 'you can`t ask questions'}, status=status.HTTP_200_OK)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        GroupService(request.user, 1, 'up', True).execute()
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def get_question_count_per_month(self, user):
        count = user.rating//100 + 5
        return count

    def get_question_list(self, user):
        count = self.get_question_count_per_month(user)
        questions = Question.objects.filter(user_id=user.id).order_by('-id')[:count][::-1]
        if questions:
            return questions
        else:
            return None

    def check(self, user):
        question_list = self.get_question_list(user)
        if question_list:
            obj = question_list[0]
            current_count = len(question_list)
            max_count = self.get_question_count_per_month(user)
            time_count = timedelta(days=30)
            created, now = self.get_date_create(obj)

            if current_count < max_count:
                return None

            if time_count <= now-created and current_count <= max_count:
                return None
            else:
                return True
        else:
            return None

    def get_date_create(self, obj):
        date = datetime.strptime(obj.date_create.strftime("%b %d %Y %H:%M:%S"), "%b %d %Y %H:%M:%S")
        now = datetime.strptime(datetime.now().strftime("%b %d %Y %H:%M:%S"), "%b %d %Y %H:%M:%S")
        return date, now


########################################################################################################################


class AnswerListViewSet(ModelViewSet):
    queryset = Answer.objects.all()
    permission_classes = (IsAuthenticatedOrReadOnly, )
    serializer_class = AnswerModuleSerializer


class AnswerCreateView(ModelViewSet):
    queryset = Answer.objects.all()
    permission_classes = (IsAuthenticated, )
    serializer_class = AnswerCreateSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        GroupService(request.user, 1, 'up', True).execute()
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class AnswerUpdateViewSet(ModelViewSet):
    queryset = Answer.objects.all()
    permission_classes = (IsAuthenticated, IsOwner)
    serializer_class = AnswerCreateSerializer

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        answer = Answer.objects.get(id=request.data['id'])
        title = request.data.get('title')
        body = request.data.get('body')
        if title:
            answer.title = title
        if body:
            answer.body = body
        answer.save()
        return Response({'detail': ('ok')}, status=status.HTTP_200_OK)


########################################################################################################################


class CommentCreateViewSet(ModelViewSet):
    queryset = Comment.objects.all()
    permission_classes = (IsAuthenticatedOrReadOnly, )
    serializer_class = CommentCreateSerializer


class CommentUpdateViewSet(ModelViewSet):
    queryset = Comment.objects.all()
    permission_classes = (IsAuthenticatedOrReadOnly, IsOwner)
    serializer_class = CommentCreateSerializer

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        comment = Comment.objects.get(id=request.data['id'])
        text = request.data.get('text')
        if text:
            comment.text = text
        comment.save()
        return Response({'detail': ('ok')}, status=status.HTTP_200_OK)


########################################################################################################################


class VoteViewSet(ModelViewSet):
    queryset = Vote.objects.all()
    permission_classes = (IsAuthenticatedOrReadOnly, )
    serializer_class = VoteSerializer

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        voter = request.user
        if voter.rating < 5:
            return Response({'detail': 'you can`t vote because your rating lower than 50'}, status=status.HTTP_200_OK)
        try:
            vote = Vote.objects.get(voter=voter.id, object_id=request.data['object_id'], content_type=request.data['content_type'])
        except:
            vote = None
        if vote:
            mess = self.check_time_for_revote(vote)
            mess = self.method_with_no_name_cause_i_have_no_idea_how_to_name_it(mess, request, vote)
            return Response({'detail': mess}, status=status.HTTP_200_OK)
        mess = self.restriction_of_self_voting(request, voter)
        if request.data['detail'] == 'question' and mess is None:
            mess = self.check_item_create_time(request)
        if mess:
            return Response({'detail': mess}, status=status.HTTP_200_OK)
        result = self.create_vote(request)
        headers = self.get_success_headers(result.data)
        return Response(result.data, status=status.HTTP_201_CREATED, headers=headers)

    def method_with_no_name_cause_i_have_no_idea_how_to_name_it(self, mess, request, vote):
        if request.data['action'] == vote.action and mess is None:
            mess = self.already_voted_check(request.data['action'], vote)
        elif request.data['action'] != vote.action and mess is None:
            mess = self.change_vote_value(request, vote)
        return mess

    def restriction_of_self_voting(self, request, voter):
        owner = self.get_item_owner(request)
        if voter.id == owner.id:
            return 'it`s yours, you can`t create your item`s votes!'
        return None

    def get_item_owner(self, request):
        current_object = self.get_current_object(request)
        owner = UserProfile.objects.get(id=current_object.user_id.id)
        return owner

    def already_voted_check(self, mode, obj):
        mess = None
        if mode == 'up' and obj.action == 'up' or mode == 'down' and obj.action == 'down':
            mess = 'already voted, you can`t vote two times with one and the same result'
        return mess

    def change_vote_value(self, request, obj):
        mess = self.rate_user(request)
        self.change_action_in_vote(obj, request)
        return mess

    def change_action_in_vote(self, obj, request):
        obj.action = request.data['action']
        obj.save()
        return obj

    def create_vote(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        self.rate_user(request)
        return serializer

    def rate_user(self, request):
        owner = self.get_item_owner(request)
        if request.data['action'] == 'up':
            GroupService(owner, 1, 'up', True).execute()
            mess = 'liked'
        else:
            GroupService(owner, 1, 'down', True).execute()
            mess = 'disliked'
        return mess

    def check_item_create_time(self, request):
        current_object = self.get_current_object(request)
        date, date_now = self.convert_date(current_object)
        difference = date_now-date
        delta = timedelta(days=30)
        return self.return_result(difference, delta)

    def get_current_object(self, request):
        if request.data['detail'] == 'question':
            obj = Question.objects.get(id=request.data['object_id'])
        elif request.data['detail'] == 'answer':
            obj = Answer.objects.get(id=request.data['object_id'])
        elif request.data['detail'] == 'comment':
            obj = Comment.objects.get(id=request.data['object_id'])
        return obj

    def check_time_for_revote(self, vote):
        date, date_now = self.convert_date(vote)
        difference = date_now - date
        delta = timedelta(hours=3)
        return self.return_result(difference, delta)

    def convert_date(self, item):
        date = datetime.strptime(item.date_create.strftime("%b %d %Y %H:%M:%S"), "%b %d %Y %H:%M:%S")
        now = datetime.strptime(datetime.now().strftime("%b %d %Y %H:%M:%S"), "%b %d %Y %H:%M:%S")
        return date, now

    def return_result(self, difference, delta):
        if difference > delta:
            return 'can`t vote because of time'
        return None


########################################################################################################################


class TagViewSet(ModelViewSet):
    queryset = Tag.objects.all()
    permission_classes = (IsAuthenticatedOrReadOnly, )
    serializer_class = TagSerializer


class AddTagRelationViewSet(ModelViewSet):
    queryset = Tag.objects.all()
    permission_classes = (IsAuthenticated, )
    serializer_class = TagUpdateSerializer

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        instance = Tag.objects.get(id=request.data['id'])
        question = Question.objects.get(id=request.data['question_id'])
        instance.question_id.add(question)
        return Response({'detail': 'updated'}, status=status.HTTP_200_OK)


class TagDeleteViewSet(ModelViewSet):
    queryset = Tag.objects.all()
    permission_classes = (IsAuthenticated, )
    serializer_class = TagDeleteSerializer

    def put(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        Tag.objects.get(id=request.data['id']).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class RemoveTagRelation(ModelViewSet):
    queryset = Tag.objects.all()
    permission_classes = (IsAuthenticated, )
    serializer_class = RemoveTagRelationSerializer

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        instance = Tag.objects.get(id=request.data['id'])
        instance.question_id.remove(request.data['question_id'])
        return Response({'detail': 'updated'}, status=status.HTTP_200_OK)


########################################################################################################################


class ModeratorQuestionEditViewSet(ModelViewSet):
    queryset = Question.objects.all()
    permission_classes = (IsAuthenticated, IsModerator)
    serializer_class = ModeratorQuestionSerializer

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(data=request.data,)
        serializer.is_valid(raise_exception=True)
        updated_question = ModeratorUpdateService(instance, serializer.validated_data, request.user, 'question').execute()
        serialized_data = ModeratorQuestionSerializer(updated_question)
        return Response(serialized_data.data)

    def get_object(self):
        return Question.objects.get(id=self.request.data['id'])


class ModeratorAnswerEditViewSet(ModelViewSet):
    queryset = Answer.objects.all()
    permission_classes = (IsAuthenticated, IsModerator)
    serializer_class = ModeratorAnswerSerializer

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(data=request.data,)
        serializer.is_valid(raise_exception=True)
        updated_question = ModeratorUpdateService(instance, serializer.validated_data, request.user, 'answer').execute()
        serialized_data = ModeratorQuestionSerializer(updated_question)
        return Response(serialized_data.data)

    def get_object(self):
        return Answer.objects.get(id=self.request.data['id'])


########################################################################################################################


class SkillViewSet(ModelViewSet):
    queryset = Skill.objects.all()
    permission_classes = (IsAuthenticatedOrReadOnly, )
    filter_backends = [DjangoFilterBackend]
    filter_fields = ['user_id']
    serializer_class = SkillSerializer


class SkillUpdateViewSet(ModelViewSet):
    queryset = Skill.objects.all()
    permission_classes = (IsAuthenticatedOrReadOnly, )
    serializer_class = SkillRemoveTagRelationSerializer

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        tag = Tag.objects.get(id=serializer.validated_data['tag_id'])
        instance.tag_id.add(tag)
        response = SkillSerializer(instance)
        return Response(response.data)

    def get_object(self):
        return Skill.objects.get(id=self.request.data['id'])


class SkillCreateViewSet(ModelViewSet):
    queryset = Skill.objects.all()
    permission_classes = (IsAuthenticated, )
    serializer_class = SkillSerializer

    def create(self, request, *args, **kwargs):
        print('in create')
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        

        # return self.create(request, *args, **kwargs)
        return Response({'awdawd': 'ok'})


class SkillRemoveTagRelation(ModelViewSet):
    queryset = Skill.objects.all()
    permission_classes = (IsAuthenticated, )
    serializer_class = SkillRemoveTagRelationSerializer

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        instance = Skill.objects.get(id=request.data['id'])
        instance.tag_id.remove(request.data['tag_id'])
        return Response({'detail': 'updated'}, status=status.HTTP_200_OK)


class SkillDeleteViewSet(ModelViewSet):
    queryset = Skill.objects.all()
    permission_classes = (IsAuthenticated, )
    serializer_class = SkillSerializer

    # def put(self, request, *args, **kwargs):
    #     return self.destroy(request, *args, **kwargs)
    #
    # def destroy(self, request, *args, **kwargs):
    #     Skill.objects.get(id=request.data['id']).delete()
    #     return Response(status=status.HTTP_204_NO_CONTENT)
