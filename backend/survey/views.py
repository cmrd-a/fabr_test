from datetime import datetime

from django.shortcuts import get_object_or_404
from rest_framework import generics
from rest_framework import mixins
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticatedOrReadOnly, AllowAny, IsAdminUser
from rest_framework.response import Response

from survey.models import Survey, Question, Choice, ExtendedUser, Answer, CompletedSurvey
from survey.serializers import SurveySerializer, AvailableSurveySeruializer, QuestionSerializer, ChoiceSerializer, \
    UserSerializer, AnswerSerializer, CompletedSurveySerializer


class SurveyViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAdminUser,)
    queryset = Survey.objects.all().order_by('finish')
    serializer_class = SurveySerializer


class UserViewSet(viewsets.ModelViewSet):
    queryset = ExtendedUser.objects.all()
    serializer_class = UserSerializer


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


class AnswerCreateView2(generics.CreateAPIView):
    permission_classes = (AllowAny,)
    queryset = Answer.objects.all()
    serializer_class = AnswerSerializer

    def post(self, request, *args, **kwargs):
        try:
            user_id = request.data['user_id']
        except KeyError:
            return Response({'user': 'required'}, status=status.HTTP_400_BAD_REQUEST)

        # try:
        #     question_id = request.data['question']
        # except KeyError:
        #     return Response({'question': 'wrong id'}, status=status.HTTP_400_BAD_REQUEST)

        user, created = ExtendedUser.objects.get_or_create(user_id=user_id)
        serializer = self.serializer_class(data={
            'user': user.user_id,
            'question': request.data['question'],
            # 'text': request.data['text'],
            # 'selected_choices': request.data['selected_choices'],
        })
        # serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            question_id = request.data['question']
            question = Question.objects.get(pk=question_id)
            survey = question.survey
            if survey.start <= datetime.now().date() <= survey.finish:
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AnswerListView(generics.ListAPIView):
    permission_classes = (IsAdminUser,)
    queryset = Answer.objects.all()
    serializer_class = AnswerSerializer


class AnswerRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = (IsAdminUser,)
    queryset = Answer.objects.all()
    serializer_class = AnswerSerializer
