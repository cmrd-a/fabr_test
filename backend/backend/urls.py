from django.conf.urls import url
from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from survey.views import UserViewSet, SurveyViewSet, QuestionViewSet, AvailableChoiceViewSet, AnswerView, \
    ExtendedUserViewSet, AvailableSurveyViewSet
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView

schema_view = get_schema_view(
    openapi.Info(
        title="Snippets API",
        default_version='v1',
        description="Test description",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@snippets.local"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

router = routers.DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'ex_users', ExtendedUserViewSet)
router.register(r'surveys', SurveyViewSet)
router.register(r'available_surveys', AvailableSurveyViewSet)
router.register(r'questions', QuestionViewSet)
router.register(r'choices', AvailableChoiceViewSet)

urlpatterns = [
    path('answers/', AnswerView.as_view()),

    path('admin/', admin.site.urls),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    url(r'^', include(router.urls)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    url(r'^swagger/$', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    url(r'^redoc/$', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),

]
