from django.db import IntegrityError
from rest_framework import serializers, fields
from rest_framework.decorators import api_view
from rest_framework.validators import UniqueTogetherValidator
from survey.models import CATEGORY_CHOICES

from survey.models import Survey, Question, Choice, ExtendedUser, Answer, CompletedSurvey


class SurveySerializer(serializers.ModelSerializer):
    start = serializers.DateField(required=False)

    # survey_completed_surveys = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        model = Survey
        fields = ['id', 'name', 'description', 'start', 'finish', 'questions', 'survey_completed_surveys']
        read_only_fields = ['id', 'start', 'survey_completed_surveys', 'questions', ]

    def create(self, validated_data):
        try:
            self.validated_data['start']
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
        return super(SurveySerializer, self).update(instance, validated_data)


class AvailableSurveySeruializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(required=False)

    class Meta:
        model = Survey
        fields = ['id', 'name', 'description', 'start', 'finish', 'questions', 'user_id']
        # read_only_fields = ['id', 'name', 'description', 'start', 'finish', 'questions']


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
        if question.category == 'text':
            raise serializers.ValidationError({"wrong question category": "must be 'one' or 'many'"})
        return data


class AnswerSerializer(serializers.ModelSerializer):
    choices = ChoiceSerializer(many=True)

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
        user_id = validated_data.pop('user_id')
        user_instance, created = ExtendedUser.objects.get_or_create(user_id=user_id)
        try:
            completed_survey_instance = CompletedSurvey.objects.create(**validated_data, user=user_instance)
        except IntegrityError:
            raise serializers.ValidationError(
                'UNIQUE constraint failed: user_id, survey_id')
        return completed_survey_instance


class UserSerializer(serializers.ModelSerializer):
    user_completed_surveys = CompletedSurveySerializer(many=True)

    class Meta:
        model = ExtendedUser
        fields = ['user_id', 'user_completed_surveys']
        read_only_fields = ['user_id']
