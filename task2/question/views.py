from datetime import datetime, timedelta
# import datetime

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.permissions import IsAuthenticatedOrReadOnly, AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from profiles.models import UserProfile
from question.models import Question, Answer, Comment, Tag, Skill, Vote, ModeratorStory
from question.serializers import QuestionSerializer, TagSerializer, \
    SkillSerializer, QuestionItemSerializer, QuestionCreateSerializer, AnswerCreateSerializer, CommentCreateSerializer, \
    VoteSerializer, TagUpdateSerializer, RemoveTagRelationSerializer, TagDeleteSerializer, ModeratorQuestionSerializer, \
    ModeratorAnswerSerializer, AnswerModuleSerializer


class QuestionViewSet(ModelViewSet):
    queryset = Question.objects.all()
    permission_classes = (IsAuthenticatedOrReadOnly, )
    serializer_class = QuestionSerializer

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        check = self.check_user_id(request)
        if check:
            return check
        question = Question.objects.get(id=request.data['id'])
        title = request.data.get('title')
        body = request.data.get('body')
        if title:
            question.title = title
        if body:
            question.body = body
        question.save()
        return Response({'detail': ('ok')}, status=status.HTTP_200_OK)

    def check_user_id(self, request):
        if request.data['user_id'] != int(request.data['current_user_id']):
            return Response({'detail': ('not yours')}, status=status.HTTP_200_OK)


class QuestionItemViewSet(ModelViewSet):
    queryset = Question.objects.all()
    permission_classes = (IsAuthenticatedOrReadOnly, )
    filter_backends = [DjangoFilterBackend]
    filter_fields = ['id']
    serializer_class = QuestionItemSerializer


################################################################


class QuestionCreateView(ModelViewSet):
    queryset = Question.objects.all()
    permission_classes = (IsAuthenticatedOrReadOnly, )
    serializer_class = QuestionCreateSerializer

    def create(self, request, *args, **kwargs):
        user = UserProfile.objects.get(id=request.data['user_id'])
        check = self.check(user)
        if check:
            return Response({'detail': ('you can`t ask questions')}, status=status.HTTP_200_OK)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        user.rating += 1
        user.save()
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


####################################################################


class AnswerCreateView(ModelViewSet):
    queryset = Answer.objects.all()
    permission_classes = (IsAuthenticated, )
    serializer_class = AnswerCreateSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        user = UserProfile.objects.get(id=request.data['user_id'])
        user.rating += 1
        user.save()
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        check = self.check_user_id(request)
        if check:
            return check
        answer = Answer.objects.get(id=request.data['id'])
        title = request.data.get('title')
        body = request.data.get('body')
        if title:
            answer.title = title
        if body:
            answer.body = body
        answer.save()
        return Response({'detail': ('ok')}, status=status.HTTP_200_OK)

    def check_user_id(self, request):
        if request.data['user_id'] != int(request.data['current_user_id']):
            return Response({'detail': ('not yours')}, status=status.HTTP_200_OK)

####################################################################


class CommentViewSet(ModelViewSet):
    queryset = Comment.objects.all()
    permission_classes = (IsAuthenticatedOrReadOnly, )
    serializer_class = CommentCreateSerializer

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        check = self.check_user_id(request)
        if check:
            return check
        comment = Comment.objects.get(id=request.data['id'])
        text = request.data.get('text')
        if text:
            comment.text = text
        comment.save()
        return Response({'detail': ('ok')}, status=status.HTTP_200_OK)

    def check_user_id(self, request):
        print('in check')
        if request.data['user_id'] != int(request.data['current_user_id']):
            return Response({'detail': ('not yours')}, status=status.HTTP_200_OK)


####################################################################

class VoteViewSet(ModelViewSet):
    queryset = Vote.objects.all()
    permission_classes = (IsAuthenticatedOrReadOnly, )
    serializer_class = VoteSerializer

    def create(self, request, *args, **kwargs):
        voter = UserProfile.objects.get(id=request.data['voter'])
        if voter.rating < 50:
            return Response({'detail': 'low rating'}, status=status.HTTP_200_OK)
        try:
            is_voted = Vote.objects.get(voter=int(request.data['voter']), object_id=request.data['object_id'])
        except:
            is_voted = None
        if is_voted:
            if self.check_revote(is_voted):
                return self.check_revote(is_voted)
            result = self.is_voted_check(request.data['action'], is_voted)
            if result:
                return Response({'detail': result}, status=status.HTTP_200_OK)
            result = self.is_voted_change(request, is_voted)
            if result:
                return Response({'detail': result}, status=status.HTTP_200_OK)
        if request.data['detail'] == 'question':
            if self.check_create_time(request):
                return self.check_create_time(request)
        if self.self_check(request):
            return self.self_check(request)
        result = self.create_vote(request)
        headers = self.get_success_headers(result.data)
        return Response(result.data, status=status.HTTP_201_CREATED, headers=headers)

    def self_check(self, request):
        user = self.get_user(request)
        if int(request.data['voter']) == user.id:
            return Response({'detail': 'It`s yours!'}, status=status.HTTP_200_OK)

    def get_user(self, request):
        current_object = self.get_current_object(request)
        user = UserProfile.objects.get(id=current_object.user_id.id)
        return user

    def is_voted_check(self, mode, obj):
        mess = None
        if mode == 'up' and obj.action == 'up':
            mess = 'already liked'
        elif mode == 'down' and obj.action == 'down':
            mess = 'already disliked'
        return mess

    def is_voted_change(self, request, obj):
        mess = self.rate_user(request)
        self.reverce_action(obj)
        return mess

    def reverce_action(self, obj):
        if obj.action == 'up':
            obj.action = 'down'
        else:
            obj.action = 'up'
        obj.save()
        return obj

    def create_vote(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        res = self.perform_create(serializer)
        res.save()
        self.rate_user(request)

        return serializer

    def rate_user(self, request):
        user = self.get_user(request)
        if request.data['action'] == 'up':
            user.rating += 1
            mess = 'liked'
        else:
            user.rating -= 1
            mess = 'disliked'
        user.save()
        return mess

    def perform_create(self, serializer):
        return serializer.save()

    def check_create_time(self, request):
        create = self.get_current_object(request)
        date, date_now = self.convert(create)
        difference = date_now-date
        delta = timedelta(days=30)
        return self.return_result(difference, delta)

    def get_current_object(self, request):
        if request.data['detail'] == 'question':
            result = Question.objects.get(id=request.data['object_id'])
        elif request.data['detail'] == 'answer':
            result = Answer.objects.get(id=request.data['object_id'])
        elif request.data['detail'] == 'comment':
            result = Comment.objects.get(id=request.data['object_id'])
        return result

    def check_revote(self, voted):
        date, date_now = self.convert(voted)
        difference = date_now - date
        delta = timedelta(hours=3)
        return self.return_result(difference, delta)

    def convert(self, item):
        date = datetime.strptime(item.date_create.strftime("%b %d %Y %H:%M:%S"), "%b %d %Y %H:%M:%S")
        now = datetime.strptime(datetime.now().strftime("%b %d %Y %H:%M:%S"), "%b %d %Y %H:%M:%S")
        return date, now

    def return_result(self, difference, delta):
        if difference > delta:
            return Response({'detail': 'can`t vote because of time'}, status=status.HTTP_200_OK)
        return None


class TagViewSet(ModelViewSet):
    queryset = Tag.objects.all()
    permission_classes = (IsAuthenticatedOrReadOnly, )
    serializer_class = TagSerializer


class TagUpdateViewSet(ModelViewSet):
    queryset = Tag.objects.all()
    permission_classes = (IsAuthenticated, )
    serializer_class = TagUpdateSerializer

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        # partial = kwargs.pop('partial', False)
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
        instance = Tag.objects.get(id=request.data['id']).delete()
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


class ModeratorQuestionEditViewSet(ModelViewSet):
    queryset = Question.objects.all()
    permission_classes = (IsAuthenticated, )
    serializer_class = ModeratorQuestionSerializer

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        check = self.check_group(request)
        if check:
            return check
        question = Question.objects.get(id=request.data['id'])
        before_updated = self.get_list(question)
        title = request.data.get('title')
        body = request.data.get('body')
        if title:
            question.title = title
        if body:
            question.body = body
        question.save()
        self.save_to_story(request, question, before_updated)

        return Response({'detail': ('ok')}, status=status.HTTP_200_OK)

    def check_group(self, request):
        if request.data['group'] != 'moderator':
            return Response({'detail': ('no permissions')}, status=status.HTTP_200_OK)

    def save_to_story(self, request, question, before_updated):
        updated = self.get_list(question)
        moderator = UserProfile.objects.get(id=request.data['current_user_id'])
        ModeratorStory.objects.create(moderator=moderator, type='question', object=question.id, date=datetime.now(), before_update=before_updated, updated=updated)

    def get_list(self, question):
        query = {
            'title': question.title,
            'body': question.body
        }
        return query


class ModeratorAnswerEditViewSet(ModelViewSet):
    queryset = Answer.objects.all()
    permission_classes = (IsAuthenticated, )
    serializer_class = ModeratorAnswerSerializer

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        check = self.check_group(request)
        if check:
            return check
        answer = Answer.objects.get(id=request.data['id'])
        before_updated = self.get_list(answer)
        title = request.data.get('title')
        body = request.data.get('body')
        if title:
            answer.title = title
        if body:
            answer.body = body
        answer.save()
        self.save_to_story(request, answer, before_updated)

        return Response({'detail': ('ok')}, status=status.HTTP_200_OK)

    def check_group(self, request):
        if request.data['group'] != 'moderator':
            return Response({'detail': ('no permissions')}, status=status.HTTP_200_OK)

    def save_to_story(self, request, answer, before_updated):
        updated = self.get_list(answer)
        moderator = UserProfile.objects.get(id=request.data['current_user_id'])
        ModeratorStory.objects.create(moderator=moderator, type='answer', object=answer.id, date=datetime.now(), before_update=before_updated, updated=updated)

    def get_list(self, answer):
        query = {
            'title': answer.title,
            'body': answer.body
        }
        return query


class AnswerListViewSet(ModelViewSet):
    queryset = Answer.objects.all()
    permission_classes = (IsAuthenticatedOrReadOnly, )
    serializer_class = AnswerModuleSerializer


class SkillViewSet(ModelViewSet):
    queryset = Skill.objects.all()
    permission_classes = (AllowAny, )
    serializer_class = SkillSerializer
