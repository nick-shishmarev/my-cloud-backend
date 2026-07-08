from django.urls import path
from rest_framework.authtoken import views as auth_views
from .views import RegisterView, CustomObtainAuthToken

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('api-token-auth/', CustomObtainAuthToken.as_view(), name='api_token_auth'),
]
