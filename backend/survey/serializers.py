from django.db import IntegrityError
from rest_framework import serializers, fields
from rest_framework.decorators import api_view
from rest_framework.validators import UniqueTogetherValidator
from survey.models import CATEGORY_CHOICES
from datetime import datetime

from survey.models import Survey, Question, Choice, ExtendedUser, Answer, CompletedSurvey, \
    CATEGORY_TEXT, CATEGORY_ONE, CATEGORY_MANY


class SurveySerializer(serializers.ModelSerializer):
    start = serializers.DateField(required=False)

    class Meta:
        model = Survey
        fields = ['id', 'name', 'description', 'start', 'finish', 'questions', 'survey_completed_surveys']
        read_only_fields = ['id', 'start', 'survey_completed_surveys', 'questions', ]

    def create(self, validated_data):
        try:
            start = self.validated_data['start']
            if start >= self.validated_data['finish']:
                raise serializers.ValidationError({'finish': "'start' must be earlier then 'finish'"})
        except KeyError:
            raise serializers.ValidationError({'start': 'this field is required on create'})
        return super(SurveySerializer, self).create(validated_data)

    def update(self, instance, validated_data):
        try:
            start = self.validated_data['start']
            if instance.start != start:
                raise serializers.ValidationError({'start': 'this field cannot be changed'})
        except KeyError:
            pass
        if validated_data['finish'] <= instance.start:
            raise serializers.ValidationError({'finish': "'finish' must be later than 'start'"})
        return super(SurveySerializer, self).update(instance, validated_data)


class AvailableSurveySeruializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(required=False)

    class Meta:
        model = Survey
        fields = ['id', 'name', 'description', 'start', 'finish', 'questions', 'user_id']
        read_only_fields = ['id', 'name', 'description', 'start', 'finish', 'questions']


class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ['id', 'survey', 'text', 'category', 'choices']
        read_only_fields = ['id', ]
        extra_kwargs = {'choices': {'required': False}}


class ChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Choice
        fields = ['id', 'question', 'text']
        read_only_fields = ['id', ]

    def validate(self, data):
        question = data['question']
        if question.category == CATEGORY_TEXT:
            raise serializers.ValidationError(
                {"wrong question category": f"must be '{CATEGORY_ONE}' or '{CATEGORY_MANY}'"})
        return data


class AnswerSerializer(serializers.ModelSerializer):
    choices = ChoiceSerializer(many=True, required=False)

    class Meta:
        model = Answer
        fields = ['question', 'text', 'choices']


class CompletedSurveySerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField()
    answers = AnswerSerializer(many=True)

    class Meta:
        model = CompletedSurvey
        fields = ['user_id', 'survey', 'answers']

    def create(self, validated_data):
        # todo: проверка типа ответа
        user_id = validated_data.pop('user_id')
        user_instance, created = ExtendedUser.objects.get_or_create(user_id=user_id)
        survey = validated_data['survey']

        if CompletedSurvey.objects.filter(user=user_instance, survey=survey) or not (
                survey.start <= datetime.now().date() <= survey.finish):
            raise serializers.ValidationError('this survey is not available')

        survey_q_id_list = list(Question.objects.filter(survey=survey).values_list('id', flat=True))
        answers_data_list = validated_data.pop('answers')
        answers_data_q_id_list = [a['question'].id for a in answers_data_list]

        if survey_q_id_list == answers_data_q_id_list:
            answers = []
            for answer_data in answers_data_list:
                answers.append(Answer.objects.create(question=answer_data['question'], text=answer_data['text']))
        else:
            raise serializers.ValidationError('wrong answers list')

        completed_survey_instance = CompletedSurvey.objects.create(**validated_data, user=user_instance)
        completed_survey_instance.answers.set(answers)
        return completed_survey_instance


class UserSerializer(serializers.ModelSerializer):
    user_completed_surveys = CompletedSurveySerializer(many=True)

    class Meta:
        model = ExtendedUser
        fields = ['user_id', 'user_completed_surveys']
        read_only_fields = ['user_id']
