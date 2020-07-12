from django.db import models

CATEGORY_TEXT = 'text'
CATEGORY_ONE = 'one'
CATEGORY_MANY = 'many'
CATEGORY_CHOICES = [(CATEGORY_TEXT, 'Text'), (CATEGORY_ONE, 'One'), (CATEGORY_MANY, 'Many')]


class Survey(models.Model):
    name = models.CharField(max_length=128)
    description = models.TextField(max_length=512, blank=True, null=True)
    start = models.DateField()
    finish = models.DateField()

    def save(self, *args, **kwargs):
        if self.pk:
            existed = Survey.objects.get(pk=self.pk)
            self.start = existed.start
        super(Survey, self).save(*args, **kwargs)

    @property
    def users_complete(self):
        return self.survey_completed_surveys.count()

    class Meta:
        ordering = ['start']


class Question(models.Model):
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE, related_name='questions')
    text = models.TextField(max_length=256)
    category = models.CharField(choices=CATEGORY_CHOICES, max_length=4)


class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='choices')
    text = models.CharField(max_length=128)


class ExtendedUser(models.Model):
    user_id = models.IntegerField(primary_key=True)


class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers')
    text = models.CharField(max_length=128, blank=True, null=True)
    choices = models.ManyToManyField(Choice, blank=True)


class CompletedSurvey(models.Model):
    user = models.ForeignKey(ExtendedUser, on_delete=models.CASCADE, related_name='user_completed_surveys')
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE, related_name='survey_completed_surveys')
    answers = models.ManyToManyField(Answer, related_name='answer_completed_surveys')

    class Meta:
        unique_together = ['user', 'survey']
        ordering = ['user', 'survey']
