import secrets

from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.mail import send_mail
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import (CreateView, DetailView, ListView, UpdateView,
                                  View)

from config.settings import EMAIL_HOST_USER
from users.forms import (UserProfileForm, UserProfileReadOnlyForm,
                         UserRegisterForm)
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


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    """
    Редактирование ТОЛЬКО своего профиля.
    """

    model = CustomUser
    form_class = UserProfileForm
    template_name = "users/profile_form.html"
    slug_field = "slug"
    slug_url_kwarg = "slug"

    def dispatch(self, request, *args, **kwargs):
        """Запрещаем редактировать чужой профиль"""
        user_obj = self.get_object()
        if user_obj != request.user:
            from django.core.exceptions import PermissionDenied

            raise PermissionDenied("Вы можете редактировать только свой профиль")
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Редактирование профиля"
        context["button_text"] = "Сохранить изменения"
        context["cancel_url"] = reverse_lazy(
            "users:profile_detail", kwargs={"slug": self.get_object().slug}
        )
        return context

    def form_valid(self, form):
        messages.success(self.request, "Профиль успешно обновлён!")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy(
            "users:profile_detail", kwargs={"slug": self.get_object().slug}
        )


class ProfileDetailView(LoginRequiredMixin, DetailView):
    """
    Просмотр профиля (своего или чужого для менеджера).
    """

    model = CustomUser
    template_name = "users/profile_detail.html"
    context_object_name = "user_obj"
    slug_field = "slug"
    slug_url_kwarg = "slug"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_obj = self.get_object()
        context["is_owner"] = user_obj == self.request.user
        context["is_manager"] = self.request.user.is_manager_user
        return context

    def dispatch(self, request, *args, **kwargs):
        user_obj = self.get_object()

        if not request.user.is_authenticated:
            raise Http404("Страница не найдена")

        # Суперпользователь может всё
        if request.user.is_superuser:
            return super().dispatch(request, *args, **kwargs)

        # Менеджер может смотреть чужие профили
        if user_obj != request.user and not request.user.is_manager_user:
            raise Http404("Страница не найдена")

        return super().dispatch(request, *args, **kwargs)


# LoginRequiredMixin проверяет, вошёл ли пользователь
# UserPassesTestMixin проверяет, имеет ли право пользователь
class UserListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    """
    Список пользователей сервиса.
    Доступен только админам и суперпользователям
    """

    model = CustomUser
    template_name = "users/user_list.html"
    context_object_name = "users"
    ordering = ["-date_joined"]  # Сначала новые пользователи
    paginate_by = 20

    def test_func(self):
        """
        Проверка, имеет ли пользователь право видеть список.
        Только менеджеры и суперпользователи.
        """

        user = self.request.user
        return user.is_manager_user or user.is_superuser

    def handle_no_permission(self):
        """Если нет прав - показываем ошибку 403"""
        from django.core.exceptions import PermissionDenied

        raise PermissionDenied("У вас нет доступа к списку пользователей")


@user_passes_test(lambda u: u.is_manager_user or u.is_superuser)
def block_user(request, pk):
    """
    Блокировка/разблокировка пользователя.
    Доступно только для менеджеров и суперпользователей.
    """
    user_to_block = get_object_or_404(CustomUser, id=pk)

    # Нельзя заблокировать самого себя
    if user_to_block == request.user:
        messages.error(request, "Вы не можете заблокировать самого себя.")
        return redirect("users:user_list")

    # Переключаем статус: если активен → блокируем, если заблокирован → разблокируем
    user_to_block.is_active = not user_to_block.is_active
    user_to_block.save()

    # Сообщение пользователю
    if user_to_block.is_active:
        messages.success(request, f"Пользователь {user_to_block.email} разблокирован.")
    else:
        messages.success(request, f"Пользователь {user_to_block.email} заблокирован.")

    return redirect("users:user_list")
