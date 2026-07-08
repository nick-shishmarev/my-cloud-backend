from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


# Форма для создания нового пользователя (в админке кнопка "Add User")
class CustomUserCreationForm(BaseUserAdmin.add_form.__class__):
    # Можно добавить кастомные поля сюда, если нужно при создании
    pass


# Форма для изменения пользователя
class CustomUserChangeForm(BaseUserAdmin.form.__class__):
    pass


@admin.register(User)
class CustomUserAdmin(BaseUserAdmin):
    # Поля, которые будут отображаться в списке пользователей в админке
    list_display = ('username', 'fullname', 'is_staff', 'is_active')

    # Поля поиска (например, по телефону или email)
    search_fields = ('username', 'fullname', 'email')

    # Фильтры справа (активен ли, staff ли и т.д.)
    list_filter = ('is_staff', 'is_active', 'is_superuser')

    fieldsets = BaseUserAdmin.fieldsets + (
        (None, {'fields': ('fullname',)}), 
    )

    # Поля, которые видны ТОЛЬКО при создании нового пользователя (не при редактировании)
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        (None, {'fields': ('fullname',)}),
    )
