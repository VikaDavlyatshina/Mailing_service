from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    """Кастомная админка пользователя"""

    # ========== СПИСОК ПОЛЬЗОВАТЕЛЕЙ ==========
    list_display = (
        "email",
        "username",
        "first_name",
        "last_name",
        "is_staff",
        "is_active",
    )

    list_filter = ("is_staff", "is_active", "groups")
    search_fields = ("email", "username", "first_name", "last_name")
    list_editable = ("is_active",)  # Можно быстро менять прямо в списке!

    # ========== ПОЛЯ ПРИ РЕДАКТИРОВАНИИ ==========
    fieldsets = (
        # Логин и пароль
        (None, {"fields": ("email", "password")}),
        # Личная информация
        (
            "Личная информация",
            {
                "fields": ("username", "first_name", "last_name", "phone", "avatar"),
            },
        ),
        # Права доступа
        (
            "Права доступа",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        # Важные даты (только чтение)
        (
            "Важные даты",
            {
                "fields": ("date_joined", "last_login"),
                "classes": ("collapse",),  # Свёрнуто по умолчанию
            },
        ),
    )

    # Поля, которые нельзя редактировать
    readonly_fields = ("date_joined", "last_login")

    # ========== ПОЛЯ ПРИ СОЗДАНИИ ==========
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "password1", "password2"),
            },
        ),
        (
            "Дополнительно",
            {
                "classes": ("wide",),
                "fields": ("first_name", "last_name", "username", "phone"),
            },
        ),
    )

    ordering = ("email",)
