from django.db.models import ProtectedError
from rest_framework import generics, status
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.response import Response
from rest_framework.authtoken.models import Token

from .serializers import RegisterSerializer, User, UsersSerializer


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


# Получение токена и user при логине
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


# Список пользователей
class UsersView(generics.ListAPIView):
    serializer_class = UsersSerializer
    queryset = User.objects.all()


# Обработка заданного пользователя (для админа)
class UsersRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = UsersSerializer
    queryset = User.objects.all()

    # Проверка наличия у пользователя файлов при удалении
    def destroy(self, request, *args, **kwargs):
        try:
            return super().destroy(request, *args, **kwargs)
        except ProtectedError as protected_error:
            protected_elements = [
                {"id": obj.pk, "label": str(obj)}
                for obj in protected_error.protected_objects
            ]
            return Response(
                data={"protected_elements": protected_elements},
                status=status.HTTP_423_LOCKED
            )

