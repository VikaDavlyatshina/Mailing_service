from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path, reverse_lazy

from users.apps import UsersConfig
from users.forms import UserLoginForm
from users.views import EmailConfirmView, ProfileView, UserCreateView

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
    path("profile/<slug:slug>/", ProfileView.as_view(), name="profile"),
]
