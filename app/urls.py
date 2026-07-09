from django.urls import path
from .views import RegisterView, CustomObtainAuthToken, UsersView, FilesView, \
    FileDetailView, DownloadFileView, UsersRetrieveUpdateDestroyView, FilesByUserForAdminView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('api-token-auth/', CustomObtainAuthToken.as_view(), name='api_token_auth'),
    path('users/', UsersView.as_view(), name='users'),
    path('users/<int:pk>', UsersRetrieveUpdateDestroyView.as_view(), name='users2'),
    path("users/<int:pk>/files/", FilesByUserForAdminView.as_view(), name="user-files-list"),
    path("files/", FilesView.as_view(), name="user-files-list-create"),
    path("files/<int:pk>/", FileDetailView.as_view(), name="user-file-detail"),
    path('files/<int:pk>/download/', DownloadFileView.as_view(), name='download-file'),
]
