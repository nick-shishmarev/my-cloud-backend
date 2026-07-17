import re

from rest_framework import serializers
from django.contrib.auth import get_user_model

from app.models import File

User = get_user_model()

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'fullname']

    def validate_username(self, value):
        pattern = r"^[A-Za-z][A-Za-z0-9]+$"

        if len(value) < 4 or len(value) > 20:
            raise serializers.ValidationError("Недопустимая длина логина")

        if not re.match(pattern, value):
            raise serializers.ValidationError("Недопустимый формат логина")

        return value

    def validate_password(self, value):
        if len(value) < 6:
            raise serializers.ValidationError("Длина пароля < 6 смволов")

        if not any(c.isupper() for c in value):
            raise serializers.ValidationError("В пароле требуется хотя бы одна заглавная буква.")

        if not any(c.islower() for c in value):
            raise serializers.ValidationError("В пароле требуется хотя бы одна строчная буква.")

        if not any(c.isdigit() for c in value):
            raise serializers.ValidationError("В пароле требуется хотя бы одна цифра.")

        if not re.search('[@#$%&*()<>?!]',value):
            raise serializers.ValidationError("В пароле требуется хотя бы один спецсимвол.")

        return value

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User.objects.create_user(**validated_data, password=password)

        return user

    def get_token(self, obj):
        return getattr(obj, 'token', None).key if hasattr(obj, 'token') else None

		
class UsersSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'fullname','directory','is_staff']


class FileSerializer(serializers.ModelSerializer):
    public_url = serializers.CharField(source='file.url', read_only=True)

    class Meta:
        model = File
        fields = [
            "id", "file", "original_name", "display_name", "comment", "size_bytes",
            "created_at", "downloaded_at", "owner", "public_url"
        ]
        read_only_fields = ["owner", "size_bytes", "created_at", "downloaded_at", "public_url"]

    def create(self, validated_data):
        request = self.context.get("request")
        if not request:
            raise serializers.ValidationError("В контексте нет request")

        owner = request.user

        file_obj = validated_data["file"]

        print(validated_data)

        validated_data["owner"] = owner
        validated_data["original_name"] = file_obj.name
        validated_data["size_bytes"] = file_obj.size
        if "display_name" not in validated_data or not validated_data["display_name"]:
            validated_data["display_name"] = file_obj.name

        return super().create(validated_data)
