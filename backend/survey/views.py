from datetime import datetime

from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly, AllowAny, IsAdminUser
from rest_framework.response import Response

from survey.models import Survey, Question, Choice, ExtendedUser, Answer, CompletedSurvey
from survey.serializers import SurveySerializer, AvailableSurveySeruializer, QuestionSerializer, ChoiceSerializer, \
    UserSerializer, AnswerSerializer, CompletedSurveySerializer, SurveyDetailsSerializer, UserDetailsSerializer


class SurveyViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAdminUser,)
    queryset = Survey.objects.all()

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return SurveyDetailsSerializer
        return SurveySerializer


class UserViewSet(viewsets.ModelViewSet):
    queryset = ExtendedUser.objects.all()

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return UserDetailsSerializer
        return UserSerializer


class AvailableSurveyViewSet(viewsets.ViewSet):
    queryset = Survey.objects.filter(
        finish__gte=datetime.now().date(),
        start__lte=datetime.now().date()
    ).order_by('finish')
    serializer_class = AvailableSurveySeruializer

    def list(self, request):
        queryset = self.queryset
        user_id = request.query_params.get('user_id')
        if user_id:
            queryset = self.queryset.exclude(survey_completed_surveys__user_id=user_id)
        serializer = AvailableSurveySeruializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        queryset = self.queryset
        user_id = request.query_params.get('user_id')
        if user_id:
            queryset = self.queryset.exclude(survey_completed_surveys__user_id=user_id)
        survey = get_object_or_404(queryset, pk=pk)
        serializer = AvailableSurveySeruializer(survey)
        return Response(serializer.data)


class QuestionViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticatedOrReadOnly,)
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer


class ChoiceViewSet(viewsets.ModelViewSet):
    queryset = Choice.objects.all()
    serializer_class = ChoiceSerializer


class AnswerViewSet(viewsets.ModelViewSet):
    permission_classes = (AllowAny,)
    queryset = Answer.objects.all()
    serializer_class = AnswerSerializer


class CompletedSurveyViewSet(viewsets.ModelViewSet):
    permission_classes = (AllowAny,)
    queryset = CompletedSurvey.objects.all()
    serializer_class = CompletedSurveySerializer
