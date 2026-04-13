from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from users.models import CustomUser

# Register your models here.


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    """
    Настройка отображения кастомной модели пользователя в админке.
    """

    # Поля, отображаемые в списке пользователей
    list_display = (
        "email",
        "username",
        "first_name",
        "last_name",
        "is_staff",
        "is_active",
    )

    # Фильтры в правой боковой панели
    list_filter = ("is_staff", "is_active", "is_superuser", "date_joined")

    # Поля для поиска
    search_fields = ("email", "username", "first_name", "last_name")

    # Количество записей на странице
    list_per_page = 25

    # Поля, которые можно редактировать прямо в списке
    list_editable = ("is_active",)

    # Порядок сортировки по умолчанию
    ordering = ("-date_joined",)
