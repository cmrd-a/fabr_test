from django.db import models


class ExtendedUser(models.Model):
    user_id = models.IntegerField(primary_key=True)


class Survey(models.Model):
    name = models.CharField(max_length=128)
    description = models.TextField(max_length=512)
    start = models.DateField(auto_now_add=True)
    finish = models.DateField()

    def check_dates(self):
        pass


class Question(models.Model):
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE, related_name='questions')
    text = models.TextField(max_length=256)
    CATEGORY_CHOICES = [('text', 'Text'), ('one', 'One'), ('many', 'Many')]
    category = models.CharField(choices=CATEGORY_CHOICES, max_length=4)


class AvailableChoice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='available_choices')
    text = models.CharField(max_length=32)


class Answer(models.Model):
    ex_user = models.ForeignKey(ExtendedUser, on_delete=models.CASCADE, null=True, blank=True, related_name='answers')
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers')
    text = models.CharField(max_length=128, blank=True, null=True)
    selected_choices = models.ManyToManyField(AvailableChoice, blank=True)

    class Meta:
        unique_together = ['ex_user', 'question']

