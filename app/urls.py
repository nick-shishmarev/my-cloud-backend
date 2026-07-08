from django.urls import path
from rest_framework.authtoken import views as auth_views
from .views import RegisterView, CustomObtainAuthToken, UsersView, UsersRetrieveUpdateDestroyView


class FilesByUserForAdminView:
    pass


urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('api-token-auth/', CustomObtainAuthToken.as_view(), name='api_token_auth'),
    path('users/', UsersView.as_view(), name='users'),
    path('users/<int:pk>', UsersRetrieveUpdateDestroyView.as_view(), name='users2'),
]
