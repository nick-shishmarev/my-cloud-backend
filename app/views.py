from rest_framework import generics, status
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.response import Response
from rest_framework.authtoken.models import Token

from .serializers import RegisterSerializer


# Регистрация нового пользователя
class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = []

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.save()
        token, _ = Token.objects.get_or_create(user=user)

        return Response({
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'fullname': user.fullname,
            },
            'token': token.key,
        }, status=status.HTTP_201_CREATED)


			
class CustomObtainAuthToken(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']

        token, _ = Token.objects.get_or_create(user=user)

        return Response({
            'token': token.key,
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'fullname': user.fullname,
                'is_staff': user.is_staff,
            },
        })
