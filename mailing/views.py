from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.cache import cache
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import (CreateView, DeleteView, DetailView, ListView,
                                  TemplateView, UpdateView)

from config import settings
from mailing.forms import MailingForm, MessageForm, RecipientForm
from mailing.models import Mailing, MailingAttempt, Message, Recipient


# ==================== MIXIN ====================
class OwnerMixin:
    """
    Миксин для автоматической фильтрации по владельцу.

    Что делает:
    - Менеджер (в группе "Менеджеры") → видит ВСЕ объекты
    - Обычный пользователь → видит ТОЛЬКО СВОИ объекты (где owner = текущий пользователь)
    - При создании объекта → автоматически прописывает owner = текущий пользователь
    """

    def get_queryset(self):
        """
        Фильтруем список объектов в зависимости от прав пользователя.
        """
        user = self.request.user

        # Если пользователь не авторизован → возвращаем пустой список
        if not user.is_authenticated:
            return self.model.objects.none()

        # Менеджер → видит ВСЕ объекты
        if user.is_superuser or user.is_manager_user:
            return self.model.objects.all()

        # Обычный пользователь → видит только свои объекты
        return self.model.objects.filter(owner=user)

    def form_valid(self, form):
        """
        Вызывается, когда форма прошла валидацию и данные корректны.
        Автоматически прописываем владельца перед сохранением.
        """
        # Проверка if form is not None нужна для DeleteView
        if form is not None:
            form.instance.owner = self.request.user
        return super().form_valid(form)


class OwnerOnlyMixin:
    """
    Миксин для редактирования и удаления.
    Пользователь может редактировать и удалять только своё
    """

    def get_queryset(self):
        """Возвращаем только свои объекты"""
        return self.model.objects.filter(owner=self.request.user)


# ==================== ПОЛУЧАТЕЛИ ====================


class RecipientCreateView(LoginRequiredMixin, OwnerMixin, CreateView):
    """Создание нового получателя рассылки"""

    model = Recipient
    form_class = RecipientForm
    template_name = "includes/form.html"
    success_url = reverse_lazy("mailing:recipient_list")

    def get_context_data(self, **kwargs):
        """Передаём дополнительные данные в шаблон"""
        context = super().get_context_data(**kwargs)
        context["title"] = "Создание получателя"
        context["cancel_url"] = reverse_lazy("mailing:recipient_list")
        return context

    def form_valid(self, form):
        """Форма валидна, сохраняем и показываем зелёное сообщение"""
        response = super().form_valid(form)
        messages.success(
            self.request, f'✅ Получатель "{self.object.email}" успешно создан!'
        )
        return response

    def form_invalid(self, form):
        """Форма невалидна, показываем красное сообщение"""
        messages.error(
            self.request,
            "❌ Ошибка при создании получателя! Проверьте правильность заполнения полей.",
        )
        return super().form_invalid(form)


class RecipientUpdateView(LoginRequiredMixin, OwnerOnlyMixin, UpdateView):
    """Редактирование существующего получателя"""

    model = Recipient
    form_class = RecipientForm
    template_name = "includes/form.html"
    success_url = reverse_lazy("mailing:recipient_list")

    def get_context_data(self, **kwargs):
        """Передаём дополнительные данные в шаблон"""
        context = super().get_context_data(**kwargs)
        context["title"] = f"✏️ Редактирование: {self.object.email}"
        context["cancel_url"] = reverse_lazy(
            "mailing:recipient_detail", kwargs={"pk": self.object.pk}
        )
        context["button_text"] = "Сохранить изменения"
        return context

    def form_valid(self, form):
        """Форма валидна, сохраняем изменения"""
        response = super().form_valid(form)
        messages.success(
            self.request, f'✏️ Получатель "{self.object.email}" успешно обновлён!'
        )
        return response

    def form_invalid(self, form):
        """Форма невалидна"""
        messages.error(
            self.request,
            "❌ Ошибка при обновлении получателя! Проверьте правильность заполнения полей.",
        )
        return super().form_invalid(form)


class RecipientListView(LoginRequiredMixin, OwnerMixin, ListView):
    """Просмотр списка получателей"""

    model = Recipient
    template_name = "mailing/recipient_list.html"
    context_object_name = "recipients"  # Имя переменной в шаблоне


class RecipientDetailView(LoginRequiredMixin, OwnerMixin, DetailView):
    """Детальный просмотр одного получателя"""

    model = Recipient
    template_name = "mailing/recipient_detail.html"
    context_object_name = "recipient"


class RecipientDeleteView(LoginRequiredMixin, OwnerOnlyMixin, DeleteView):
    """
    Удаление получателя.
    """

    model = Recipient
    template_name = "includes/confirm_delete.html"
    success_url = reverse_lazy("mailing:recipient_list")

    def get_context_data(self, **kwargs):
        """Передаём URL для кнопки Отмена"""
        context = super().get_context_data(**kwargs)
        context["cancel_url"] = reverse_lazy(
            "mailing:recipient_detail", kwargs={"pk": self.object.pk}
        )
        return context

    def delete(self, request, *args, **kwargs):
        """Удаляем и показываем сообщение"""
        self.object = self.get_object()
        email = self.object.email  # Сохраняем email до удаления
        messages.success(request, f'🗑️ Получатель "{email}" успешно удалён!')
        return super().delete(request, *args, **kwargs)


# ==================== СООБЩЕНИЯ ====================


class MessageCreateView(LoginRequiredMixin, OwnerMixin, CreateView):
    """Создание нового сообщения для рассылки"""

    model = Message
    form_class = MessageForm
    template_name = "includes/form.html"
    success_url = reverse_lazy("mailing:message_list")

    def get_context_data(self, **kwargs):
        """Передаём дополнительные данные в шаблон"""
        context = super().get_context_data(**kwargs)
        context["title"] = "📝 Создание сообщения"
        context["cancel_url"] = reverse_lazy("mailing:message_list")
        context["button_text"] = "Создать сообщение"
        return context

    def form_valid(self, form):
        """Сообщение создано"""
        response = super().form_valid(form)
        messages.success(
            self.request, f'✅ Сообщение "{self.object.subject}" успешно создано!'
        )
        return response

    def form_invalid(self, form):
        """Форма невалидна"""
        messages.error(
            self.request,
            "❌ Ошибка при создании сообщения! Проверьте правильность заполнения полей.",
        )
        return super().form_invalid(form)


class MessageUpdateView(LoginRequiredMixin, OwnerOnlyMixin, UpdateView):
    """Редактирование существующего сообщения"""

    model = Message
    form_class = MessageForm
    template_name = "includes/form.html"
    success_url = reverse_lazy("mailing:message_list")

    def get_context_data(self, **kwargs):
        """Передаём дополнительные данные в шаблон"""
        context = super().get_context_data(**kwargs)
        context["title"] = f"✏️ Редактирование: {self.object.subject}"
        context["cancel_url"] = reverse_lazy(
            "mailing:message_detail", kwargs={"pk": self.object.pk}
        )
        context["button_text"] = "Сохранить изменения"
        return context

    def form_valid(self, form):
        """Сообщение обновлено"""
        response = super().form_valid(form)
        messages.success(
            self.request, f'✏️ Сообщение "{self.object.subject}" успешно обновлено!'
        )
        return response

    def form_invalid(self, form):
        """Форма невалидна"""
        messages.error(
            self.request,
            "❌ Ошибка при обновлении сообщения! Проверьте правильность заполнения полей.",
        )
        return super().form_invalid(form)


class MessageDeleteView(LoginRequiredMixin, OwnerOnlyMixin, DeleteView):
    """Удаление сообщения"""

    model = Message
    template_name = "includes/confirm_delete.html"
    success_url = reverse_lazy("mailing:message_list")

    def get_context_data(self, **kwargs):
        """Передаём URL для кнопки Отмена"""
        context = super().get_context_data(**kwargs)
        context["cancel_url"] = reverse_lazy(
            "mailing:message_detail", kwargs={"pk": self.object.pk}
        )
        return context

    def delete(self, request, *args, **kwargs):
        """Сообщение удалено"""
        self.object = self.get_object()
        subject = self.object.subject  # Сохраняем тему до удаления
        messages.success(request, f'🗑️ Сообщение "{subject}" успешно удалено!')
        return super().delete(request, *args, **kwargs)


class MessageListView(LoginRequiredMixin, OwnerMixin, ListView):
    """Просмотр списка сообщений"""

    model = Message
    template_name = "mailing/message_list.html"
    context_object_name = "message_list"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["user"] = self.request.user
        return context


class MessageDetailView(LoginRequiredMixin, OwnerMixin, DetailView):
    """Детальный просмотр одного сообщения"""

    model = Message
    template_name = "mailing/message_detail.html"
    context_object_name = "message"


# ==================== РАССЫЛКИ ====================


class MailingCreateView(LoginRequiredMixin, OwnerMixin, CreateView):
    """Создание новой рассылки"""

    model = Mailing
    form_class = MailingForm
    template_name = "includes/form.html"
    success_url = reverse_lazy("mailing:mailing_list")

    def get_context_data(self, **kwargs):
        """Передаём дополнительные данные в шаблон"""
        context = super().get_context_data(**kwargs)
        context["title"] = "📨 Создание рассылки"
        context["cancel_url"] = reverse_lazy("mailing:mailing_list")
        context["button_text"] = "Создать рассылку"
        return context

    def form_valid(self, form):
        """Рассылка создана"""
        response = super().form_valid(form)
        messages.success(
            self.request, f"✅ Рассылка #{self.object.id} успешно создана!"
        )
        return response

    def form_invalid(self, form):
        """❌ ОШИБКА: форма невалидна (например, дата начала в прошлом)"""
        messages.error(
            self.request,
            "❌ Ошибка при создании рассылки! Проверьте даты и правильность заполнения полей.",
        )
        return super().form_invalid(form)


class MailingUpdateView(LoginRequiredMixin, OwnerOnlyMixin, UpdateView):
    """Редактирование существующей рассылки"""

    model = Mailing
    form_class = MailingForm
    template_name = "includes/form.html"
    success_url = reverse_lazy("mailing:mailing_list")

    def get_context_data(self, **kwargs):
        """Передаём дополнительные данные в шаблон"""
        context = super().get_context_data(**kwargs)
        context["title"] = (
            f"✏️ Редактирование рассылки #{self.object.id} - {self.object.message.subject}"
        )
        context["cancel_url"] = reverse_lazy(
            "mailing:mailing_detail", kwargs={"pk": self.object.pk}
        )
        context["button_text"] = "Сохранить изменения"
        return context

    def form_valid(self, form):
        """Рассылка обновлена"""
        response = super().form_valid(form)
        messages.success(
            self.request, f"✏️ Рассылка #{self.object.id} успешно обновлена!"
        )
        return response

    def form_invalid(self, form):
        """❌ ОШИБКА: форма невалидна"""
        messages.error(
            self.request,
            "❌ Ошибка при обновлении рассылки! Проверьте даты и правильность заполнения полей.",
        )
        return super().form_invalid(form)


class MailingDeleteView(LoginRequiredMixin, OwnerOnlyMixin, DeleteView):
    """Удаление рассылки"""

    model = Mailing
    template_name = "includes/confirm_delete.html"
    success_url = reverse_lazy("mailing:mailing_list")

    def get_context_data(self, **kwargs):
        """Передаём URL для кнопки Отмена"""
        context = super().get_context_data(**kwargs)
        context["cancel_url"] = reverse_lazy(
            "mailing:mailing_detail", kwargs={"pk": self.object.pk}
        )
        return context

    def delete(self, request, *args, **kwargs):
        """Рассылка удалена"""
        self.object = self.get_object()
        mailing_id = self.object.id  # Сохраняем ID до удаления
        messages.success(request, f"🗑️ Рассылка #{mailing_id} успешно удалена!")
        return super().delete(request, *args, **kwargs)


class MailingListView(LoginRequiredMixin, OwnerMixin, ListView):
    """Просмотр списка рассылок"""

    model = Mailing
    template_name = "mailing/mailing_list.html"
    context_object_name = "mailings"

    def get_queryset(self):
        queryset = super().get_queryset()
        # Обновляем статус каждой рассылки
        for mailing in queryset:
            mailing.update_status()
        return queryset


class MailingDetailView(LoginRequiredMixin, OwnerMixin, DetailView):
    """Детальный просмотр одной рассылки"""

    model = Mailing
    template_name = "mailing/mailing_detail.html"
    context_object_name = "mailing"


def run_mailing(request, pk):
    """
    Ручной запуск рассылки по нажатию кнопки.

    Алгоритм:
    1. Находим рассылку по ID
    2. Проверяем, что статус 'launched' (текущее время между start_time и end_time)
    3. Для каждого получателя:
       - Отправляем письмо через send_mail()
       - Сохраняем попытку в MailingAttempt (успех или ошибка)
    4. Показываем итоговую статистику
    """

    # 1. Находим рассылку или выдаём 404
    mailing = get_object_or_404(Mailing, id=pk)

    # 2. Проверяем, можно ли отправлять (статус должен быть 'launched')
    if mailing.get_dynamic_status() != "launched":
        messages.error(
            request,
            f'❌ Нельзя запустить рассылку со статусом "{mailing.get_status_display()}". '
            f"Отправка возможна только в период с {mailing.start_time} по {mailing.end_time}.",
        )
        return redirect("mailing:mailing_detail", pk=pk)

    # 3. Счётчики для итоговой статистики
    success_count = 0
    fail_count = 0

    # 4. Отправляем письма всем получателям
    for recipient in mailing.recipients.all():
        try:
            # Пытаемся отправить письмо
            send_mail(
                subject=mailing.message.subject,  # Тема из сообщения
                message=mailing.message.email_body,  # Тело из сообщения
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[recipient.email],  # Кому отправляем
                fail_silently=False,  # Если ошибка — выбрасываем исключение
            )
            # Если дошли сюда — отправка успешна
            status = "success"
            response = "✅ Письмо успешно отправлено"
            success_count += 1

        except Exception as e:
            # Если ошибка — сохраняем её текст
            status = "failure"
            response = f"❌ Ошибка при отправке: {str(e)}"
            fail_count += 1

        # 5. Сохраняем запись о попытке в БД
        MailingAttempt.objects.create(
            status=status,
            server_response=response,  # Текст ответа/ошибки
            mailing=mailing,  # Связь с рассылкой
            recipient=recipient,  # Кому отправляли
        )

    # 6. Показываем итоговое сообщение пользователю
    messages.success(
        request,
        f'📨 Рассылка "#{mailing.id}" завершена!\n'
        f"✅ Успешно отправлено: {success_count}\n"
        f"❌ Ошибок: {fail_count}",
    )

    # 7. Возвращаемся на страницу рассылки
    return redirect("mailing:mailing_detail", pk=pk)


class HomeView(LoginRequiredMixin, TemplateView):
    """Домашняя страница со статистикой и кешированием"""

    template_name = "mailing/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        # Ключ кеша зависит от пользователя (чтобы менеджеры и обычные пользователи не путались)
        cache_key = f"home_stats_user_{user.id}"

        # Пробуем взять данные из кеша
        stats = cache.get(cache_key)

        if stats is None:
            # Если данных в кеше нет - вычисляем

            # 1. Определяем, какие рассылки видит пользователь
            if user.is_manager_user or user.is_superuser:
                mailings = Mailing.objects.all()
                recipients_count = Recipient.objects.count()
            else:
                mailings = Mailing.objects.filter(owner=user)
                recipients_count = Recipient.objects.filter(owner=user).count()

            # 2. Общее количество рассылок
            total_mailings = mailings.count()

            # 3. Количество активных рассылок (через метод модели)
            active_count = 0
            for mailing in mailings:
                if mailing.get_dynamic_status() == "launched":
                    active_count += 1

            # 4. Статистика попыток отправки
            attempts = MailingAttempt.objects.filter(mailing__in=mailings)
            total_attempts = attempts.count()
            successful_attempts = attempts.filter(status="success").count()
            failed_attempts = attempts.filter(status="failure").count()

            # 5. Процент успешных отправок
            if total_attempts > 0:
                success_rate = round((successful_attempts / total_attempts * 100), 1)
            else:
                success_rate = 0

            # 6. Собираем всё в словарь
            stats = {
                "total_mailings": total_mailings,
                "active_mailings": active_count,
                "unique_recipients": recipients_count,
                "total_attempts": total_attempts,
                "successful_attempts": successful_attempts,
                "failed_attempts": failed_attempts,
                "success_rate": success_rate,
            }

            # 7. Сохраняем в кеш на 5 минут (300 секунд)
            cache.set(cache_key, stats, 300)

        # 8. Передаём данные в шаблон
        context.update(stats)
        return context


@user_passes_test(lambda u: u.is_manager_user or u.is_superuser)
def mailing_disable(request, pk):
    """
    Отключение рассылки менеджером.
    Доступно только для пользователей с правами менеджера.

    Что делает:
        - Меняет статус рассылки с 'launched' на 'completed'
        - Показывает сообщение об успехе
    """

    # 1. Находим рассылку или выдаём 404
    mailing = get_object_or_404(Mailing, id=pk)

    # 2. Проверяем, что рассылка запущена
    if mailing.get_dynamic_status() != "launched":
        messages.error(
            request,
            f'❌ Нельзя отключить рассылку со статусом "{mailing.get_status_display()}". '
            f"Отключать можно только запущенные рассылки.",
        )
        return redirect("mailing:mailing_detail", pk=pk)

    # 3. Обновляем статус
    Mailing.objects.filter(id=pk).update(status="completed")

    # 4. Показываем сообщение об успехе
    messages.success(
        request,
        f'🔒 Рассылка #{mailing.id} "{mailing.message.subject}" отключена менеджером.',
    )

    # 5. Возвращаемся на страницу рассылки
    return redirect("mailing:mailing_detail", pk=pk)


class LandingView(TemplateView):
    """Публичная страница (видна всем, даже неавторизованным)"""

    template_name = "mailing/landing.html"


class MailingAttemptListView(LoginRequiredMixin, ListView):
    """Список всех попыток рассылок"""

    model = MailingAttempt
    template_name = "mailing/mailing_attempt_list.html"
    context_object_name = "attempts"
    ordering = ["-attempt_time"]  # Сначала новые

    def get_queryset(self):
        user = self.request.user
        if user.is_manager_user or user.is_superuser:
            return MailingAttempt.objects.all()
        # Обычный пользователь видит только попытки своих рассылок
        return MailingAttempt.objects.filter(mailing__owner=user)
