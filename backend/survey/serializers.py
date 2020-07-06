from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.decorators import api_view

from survey.models import ExtendedUser, Survey, Question, Answer, AvailableChoice


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username']
        read_only_fields = ['id', ]


class ExtendedUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExtendedUser
        fields = ['user_id', 'answers']
        read_only_fields = ['user_id', 'answers']
        depth = 3


class SurveySerializer(serializers.ModelSerializer):
    class Meta:
        model = Survey
        fields = ['id', 'name', 'description', 'start', 'finish', 'questions']
        read_only_fields = ['id', 'start']
        extra_kwargs = {'questions': {'required': False}}


class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ['id', 'survey', 'text', 'category', 'available_choices']
        read_only_fields = ['id', ]
        extra_kwargs = {'available_choices': {'required': False}}


class AvailableChoiceSerializer(serializers.ModelSerializer):
    def validate(self, data):
        question = data['question']
        if question.category == 'text':
            raise serializers.ValidationError({"wrong question category": "must be 'one' or 'many'"})
        return data

    class Meta:
        model = AvailableChoice
        fields = ['id', 'question', 'text']
        read_only_fields = ['id', ]


class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = ['id', 'ex_user', 'question', 'text', 'selected_choices']
        read_only_fields = ['id', ]
        extra_kwargs = {'text': {'required': False}}
