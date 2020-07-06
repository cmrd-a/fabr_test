from django.contrib import admin
from .models import Survey, Answer, Question, AvailableChoice, ExtendedUser

admin.site.register(ExtendedUser)
admin.site.register(Survey)
admin.site.register(Answer)
admin.site.register(Question)
admin.site.register(AvailableChoice)
