from pathlib import Path

from django.db.models import ProtectedError
from django.http import FileResponse
from django.utils import timezone
from rest_framework import generics, status
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.exceptions import PermissionDenied, NotFound
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, IsAdminUser

from .models import File
from .serializers import RegisterSerializer, User, UsersSerializer, FileSerializer


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


# Список пользователей
class UsersView(generics.ListAPIView):
    serializer_class = UsersSerializer
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated, IsAdminUser]


# Обработка заданного пользователя (для админа)
class UsersRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = UsersSerializer
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated, IsAdminUser]

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

			
class FilesView(APIView):
    permission_classes = [IsAuthenticated]

    # Список файлов текущего пользователя
    def get(self, request):
        files = File.objects.filter(owner=request.user)
        serializer = FileSerializer(files, many=True, context={"request": request})
        return Response(serializer.data)

    # Загрузка файла (multipart)
    def post(self, request):
        serializer = FileSerializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class FileDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def _get_object(self, pk):
        obj = File.objects.get(pk=pk)
        if (obj.owner != self.request.user) and not self.request.user.is_staff:
            raise PermissionDenied("Отказано в доступе - недостаточно прав")
        return obj

    # Запрос одного файл по id
    def get(self, request, pk):
        file_obj = self._get_object(pk)
        serializer = FileSerializer(file_obj, context={"request": request})
        return Response(serializer.data)

    # Замена display_name (видимое имя) и комментария
    def patch(self, request, pk):
        file_obj = self._get_object(pk)
        display_name = request.data.get("display_name")
        comment = request.data.get("comment")
		
        if display_name is not None or comment is not None:
            if display_name is not None:
                file_obj.display_name = display_name
				
            if comment is not None:
                file_obj.comment = comment

            file_obj.save(update_fields=["display_name", "comment"])
			
        serializer = FileSerializer(file_obj, context={"request": request})
        return Response(serializer.data)

    # Удалить файл (и физически, и из БД)
    def delete(self, request, pk):
        file_obj = self._get_object(pk)

        if file_obj.file and file_obj.file.path:
            file_path = Path(file_obj.file.path)
            file_path.unlink(missing_ok=True)

        file_obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

# Список файлов заданного пользователя для админа или для владельца
class FilesByUserForAdminView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        # Проверка прав: админ или сам пользователь
        if not request.user.is_staff and int(pk) != request.user.id:
            raise PermissionDenied("Отказано в доступа к хранилищу - недостаточно прав")

        files = File.objects.filter(owner_id=pk)
        serializer = FileSerializer(files, many=True, context={"request": request})
        return Response(serializer.data)


# Скачивание файла с сохранением отображаемого имени
class DownloadFileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):

        try:
            file_obj = File.objects.get(id=pk)
        except File.DoesNotExist:
            raise NotFound("Запрошенный файл не найден")

        if file_obj.owner != request.user and not request.user.is_staff:
            raise PermissionDenied("Отказано в доступа к файлу - недостаточно прав")

        file_obj.downloaded_at = timezone.now()
        file_obj.save(update_fields=["downloaded_at"])

        response = FileResponse(
            file_obj.file.open(),
            as_attachment=True,
            filename=file_obj.display_name,
        )
        return response
