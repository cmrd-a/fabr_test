from datetime import datetime

from rest_framework import serializers

from survey.models import Survey, Question, Choice, ExtendedUser, Answer, CompletedSurvey, \
    CATEGORY_TEXT, CATEGORY_ONE, CATEGORY_MANY


class SurveySerializer(serializers.ModelSerializer):
    """
    Поле "start" обязательно только при создании опроса.
    При обновлении оно может отсутсвовать или совпадать с текущим значением.
    Дата окончания должна быть позже даты начала опроса.
    """
    start = serializers.DateField(required=False)

    class Meta:
        model = Survey
        fields = ['id', 'name', 'description', 'start', 'finish', 'questions', 'users_complete']
        read_only_fields = ['id', 'start', 'questions', 'users_complete']

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
        read_only_fields = ['id']


class ChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Choice
        fields = ['id', 'question', 'text']
        read_only_fields = ['id', ]


class AnswerSerializer(serializers.ModelSerializer):
    """
    Выполняется проверка, что поля ответа соответствуют типу вопроса.
    Варианты ответа проверяются на привязку к конкретному вопросу.
    """
    choices = serializers.ListSerializer
    question = serializers.CharField(source='question.text')

    class Meta:
        model = Answer
        fields = ['question', 'text', 'choices']

    def validate(self, attrs):
        question = attrs['question']
        if question.category == CATEGORY_TEXT:
            try:
                attrs['text']
            except KeyError:
                raise serializers.ValidationError({
                    "question": question,
                    "text": 'text required'})
        else:
            try:
                choices = attrs['choices']
            except KeyError:
                raise serializers.ValidationError({
                    "question": question,
                    "choices": 'choices required'})

            question_choices_id_list = list(question.choices.values_list('id', flat=True))
            data_choices_id_list = [c.id for c in choices]

            if not set(data_choices_id_list).issubset(question_choices_id_list):
                raise serializers.ValidationError({
                    "question": question,
                    "choices": 'wrong choices list'})

            if question.category == CATEGORY_ONE and len(choices) != 1:
                raise serializers.ValidationError({
                    "question": question,
                    "choices": 'one choice required in this answer'})

            if question.category == CATEGORY_MANY and len(choices) <= 1:
                raise serializers.ValidationError({
                    "question": question,
                    "choices": 'at least two choices needed in this answer'})

        return attrs


class CompletedSurveySerializer(serializers.ModelSerializer):
    """
    Создаётся или выбирается пользователь с переданным 'user_id'.
    Выполняется проверка что полльзователь ещё не проходил этот опрос,
    и что текущая дата в рамках времени проведения опроса.
    Выполняется проверка, что даны ответы на каждый вопрос в опросе.
    В зависимости от типа вопроса, записываются нужные поля в ответ.
    """
    user_id = serializers.IntegerField()
    answers = AnswerSerializer(many=True)

    class Meta:
        model = CompletedSurvey
        fields = ['user_id', 'survey', 'answers']

    def create(self, validated_data):
        user_id = validated_data.pop('user_id')
        user_instance, created = ExtendedUser.objects.get_or_create(user_id=user_id)
        survey = validated_data['survey']

        if CompletedSurvey.objects.filter(user=user_instance, survey=survey) or not (
                survey.start <= datetime.now().date() <= survey.finish):
            raise serializers.ValidationError('this survey is not available')

        survey_q_id_list = list(Question.objects.filter(survey=survey).values_list('id', flat=True))
        answer_data_list = validated_data.pop('answers')
        answers_data_q_id_list = [a['question'].id for a in answer_data_list]

        if sorted(survey_q_id_list) == sorted(answers_data_q_id_list):
            answers = []
            for answer_data in answer_data_list:
                question = answer_data['question']
                new_answer = Answer.objects.create(question=question)
                if question.category == CATEGORY_TEXT:
                    new_answer.text = answer_data['text']
                    new_answer.save()
                elif question.category == CATEGORY_ONE or question.category == CATEGORY_MANY:
                    new_answer.choices.set(answer_data['choices'])
                answers.append(new_answer)

        else:
            raise serializers.ValidationError('wrong answers list')

        completed_survey_instance = CompletedSurvey.objects.create(**validated_data, user=user_instance)
        completed_survey_instance.answers.set(answers)
        return completed_survey_instance


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExtendedUser
        fields = ['user_id', ]


class QuestionDetailsSerializer(serializers.ModelSerializer):
    choices = ChoiceSerializer(many=True)

    class Meta:
        model = Question
        fields = ['id', 'survey', 'text', 'category', 'choices']
        read_only_fields = ['id', ]


class SurveyDetailsSerializer(serializers.ModelSerializer):
    questions = QuestionDetailsSerializer(many=True)

    class Meta:
        model = Survey
        fields = ['id', 'name', 'description', 'start', 'finish', 'questions', 'users_complete']
        read_only_fields = ['id', 'start', 'questions', 'users_complete']


class UserDetailsSerializer(serializers.ModelSerializer):
    user_completed_surveys = CompletedSurveySerializer(many=True, read_only=True)

    class Meta:
        model = ExtendedUser
        fields = ['user_id', 'user_completed_surveys']
        read_only_fields = ['user_id', 'user_completed_surveys']


class AvailableSurveyDetailsSeruializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(required=False)
    questions = QuestionDetailsSerializer(many=True)

    class Meta:
        model = Survey
        fields = ['id', 'name', 'description', 'start', 'finish', 'questions', 'user_id']
        read_only_fields = ['id', 'name', 'description', 'start', 'finish', 'questions']
