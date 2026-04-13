import secrets

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView, View

from config.settings import EMAIL_HOST_USER
from users.forms import UserProfileForm, UserRegisterForm, UserProfileReadOnlyForm
from users.models import CustomUser


class UserCreateView(CreateView):
    """Создание нового пользователя с подтверждением email"""

    model = CustomUser
    form_class = UserRegisterForm
    template_name = "users/register.html"
    success_url = reverse_lazy("users:login")

    def form_valid(self, form):
        """Сохраняем пользователя и отправляем письмо с подтверждением"""

        # Сохраняем пользователя, но НЕ активируем

        # Без commit=False пользователь сохранился бы сразу с is_active=True.
        user = form.save(commit=False)
        user.is_active = False  # Пользователь неактивен до подтверждения email
        user.save()

        # Генерируем токен и сохраняем в модель
        token = secrets.token_hex(16)
        user.token = token
        user.save()

        # Формируем ссылку для подтверждения
        host = self.request.get_host()
        verification_url = f"http://{host}/users/email-confirm/{token}/"

        # Отправляем письмо
        send_mail(
            subject="Подтверждение регистрации",
            message=f"""Здравствуйте!

Для подтверждения вашей регистрации перейдите по ссылке:
{verification_url}

Если вы не регистрировались на нашем сайте, просто проигнорируйте это письмо.

С уважением,
Команда сервиса рассылок""",
            from_email=EMAIL_HOST_USER,
            recipient_list=[user.email],
            # При разработке - видно ошибки
            # Для продакшена - использовать fail_silently=True (пользователь не увидит ошибку)
            fail_silently=False,
        )

        messages.success(
            self.request,
            "Регистрация успешна! На вашу почту отправлено письмо с ссылкой для подтверждения.",
        )

        # Сохраняем пользователя
        return super().form_valid(form)


# Используется класс View, потому что это не форма, а просто обработчик GET-запроса по ссылке из письма
class EmailConfirmView(View):
    """Подтверждение email по токену"""

    def get(self, request, token):
        """Обрабатываем GET-запрос по ссылке из письма"""

        # Находим пользователя с таким токеном (если нет — 404)
        user = get_object_or_404(CustomUser, token=token, is_active=False)

        # Активируем пользователя
        user.is_active = True
        user.token = None  # Очищаем токен (одноразовый)
        user.save()

        messages.success(
            request, "Email успешно подтверждён! Теперь вы можете войти в систему."
        )
        return redirect("users:login")


class ProfileView(LoginRequiredMixin, UpdateView):
    """
    Просмотр и редактирование профиля пользователя.

    Особенности:
    - Если пользователь смотрит свой профиль → может редактировать
    - Если менеджер смотрит чужой профиль → только просмотр
    - Если обычный пользователь смотрит чужой профиль → ошибка 403
    """

    model = CustomUser
    form_class = UserProfileForm
    template_name = "users/profile.html"

    slug_field = 'slug'
    slug_url_kwarg = 'slug'

    def get_object(self, queryset=None):
        slug = self.kwargs.get('slug')
        return get_object_or_404(CustomUser, slug=slug)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_obj = self.get_object()
        context["title"] = "Профиль пользователя"
        context["button_text"] = "Сохранить изменения"
        context["cancel_url"] = reverse_lazy("mailing:home")
        context["is_owner"] = (user_obj == self.request.user)
        context["is_manager"] = self.request.user.is_staff
        context["user_obj"] = user_obj
        return context

    def get_form_class(self):
        user_obj = self.get_object()

        # Свой профиль — можно редактировать
        if user_obj == self.request.user:
            return UserProfileForm

        # Чужой профиль для менеджера — только чтение
        if self.request.user.is_staff:
            return UserProfileReadOnlyForm

        # Обычный пользователь смотрит чужой профиль — доступ запрещён
        from django.core.exceptions import PermissionDenied
        raise PermissionDenied("У вас нет доступа к этому профилю")

    def get_template_names(self):
        user_obj = self.get_object()
        if user_obj == self.request.user:
            return ['users/profile.html']
        return ['users/public_profile.html']

    def form_valid(self, form):
        messages.success(self.request, "Профиль успешно обновлён!")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('users:profile', kwargs={'slug': self.get_object().slug})
