from django.contrib.auth.views import (LoginView, LogoutView,
                                       PasswordResetCompleteView,
                                       PasswordResetConfirmView,
                                       PasswordResetDoneView,
                                       PasswordResetView)
from django.urls import path, reverse_lazy

from users.apps import UsersConfig
from users.forms import (UserLoginForm, UserPasswordResetForm,
                         UserSetPasswordForm)
from users.views import (EmailConfirmView, ProfileDetailView,
                         ProfileUpdateView, UserCreateView, UserListView,
                         block_user)

app_name = UsersConfig.name

urlpatterns = [
    # Регистрация
    path("register/", UserCreateView.as_view(), name="register"),
    # Подтверждение email
    path(
        "email-confirm/<str:token>/", EmailConfirmView.as_view(), name="email_confirm"
    ),
    # Вход в систему
    path(
        "login/",
        LoginView.as_view(form_class=UserLoginForm, template_name="users/login.html"),
        name="login",
    ),
    # Выход из системы
    path("logout/", LogoutView.as_view(), name="logout"),
    # Профиль
    # Просмотр профиля
    path("profile/<slug:slug>/", ProfileDetailView.as_view(), name="profile_detail"),
    # Редактирование профиля (только свой)
    path(
        "profile/<slug:slug>/edit/", ProfileUpdateView.as_view(), name="profile_update"
    ),
    # Восстановление пароля
    # Шаг 1: Форма "Забыли пароль?" — ввод email
    path(
        "password-reset/",
        PasswordResetView.as_view(
            form_class=UserPasswordResetForm,
            template_name="users/password_reset.html",
            email_template_name="users/password_reset_email.html",
            success_url=reverse_lazy("users:password_reset_done"),
        ),
        name="password_reset",
    ),
    # Шаг 2: Сообщение "Письмо отправлено"
    path(
        "password-reset/done/",
        PasswordResetDoneView.as_view(template_name="users/password_reset_done.html"),
        name="password_reset_done",
    ),
    # Шаг 3: Ссылка из письма — форма ввода нового пароля
    path(
        "password-reset/<uidb64>/<token>/",
        PasswordResetConfirmView.as_view(
            form_class=UserSetPasswordForm,
            template_name="users/password_reset_confirm.html",
            success_url=reverse_lazy("users:password_reset_complete"),
        ),
        name="password_reset_confirm",
    ),
    # Шаг 4: Сообщение "Пароль успешно изменён"
    path(
        "password-reset/complete/",
        PasswordResetCompleteView.as_view(
            template_name="users/password_reset_complete.html"
        ),
        name="password_reset_complete",
    ),
    # Список пользователей (только для менеджеров)
    path("list/", UserListView.as_view(), name="user_list"),
    # Блокировка пользователя (только для менеджеров)
    path("block/<int:pk>/", block_user, name="block_user"),
]
