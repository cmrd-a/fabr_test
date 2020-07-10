from django.contrib import admin
from survey.models import Survey, Question, Choice, ExtendedUser, Answer, CompletedSurvey

admin.site.register(Survey)
admin.site.register(Question)
admin.site.register(Choice)
admin.site.register(Answer)
admin.site.register(ExtendedUser)
admin.site.register(CompletedSurvey)
