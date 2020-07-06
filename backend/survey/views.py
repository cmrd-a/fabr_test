from django.contrib.auth.models import User

from rest_framework import viewsets, status
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response

from .serializers import UserSerializer, SurveySerializer, QuestionSerializer, AvailableChoiceSerializer, \
    AnswerSerializer, ExtendedUserSerializer
from survey.models import Survey, Question, Answer, AvailableChoice, ExtendedUser
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from datetime import datetime


class UserViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer


class ExtendedUserViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticatedOrReadOnly,)
    queryset = ExtendedUser.objects.all()
    serializer_class = ExtendedUserSerializer


class SurveyViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    queryset = Survey.objects.all().order_by('finish')
    serializer_class = SurveySerializer


class AvailableSurveyViewSet(viewsets.ModelViewSet):
    queryset = Survey.objects.filter(finish__gt=datetime.now().date()).order_by('finish')
    serializer_class = SurveySerializer


class QuestionViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticatedOrReadOnly,)
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer


class AvailableChoiceViewSet(viewsets.ModelViewSet):
    queryset = AvailableChoice.objects.all()
    serializer_class = AvailableChoiceSerializer


class AnswerView(CreateAPIView):
    queryset = Answer.objects.all()
    serializer_class = AnswerSerializer

    def post(self, request, *args, **kwargs):
        ex_user_id = request.data['ex_user_id']
        ex_user, created = ExtendedUser.objects.get_or_create(user_id=ex_user_id)
        serializer = self.serializer_class(data={
            'ex_user': ex_user.user_id,
            'question': request.data['question'],
            'text': request.data['text'],
            'selected_choices': request.data['selected_choices'],
        })
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.data, status=status.HTTP_400_BAD_REQUEST)
