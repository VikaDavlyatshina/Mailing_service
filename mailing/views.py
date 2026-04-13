from django.contrib import messages
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import (CreateView, DeleteView, DetailView, ListView,
                                  TemplateView, UpdateView)

from config import settings
from mailing.forms import MailingForm, MessageForm, RecipientForm
from mailing.models import Mailing, MailingAttempt, Message, Recipient

# Create your views here.

# ==================== ПОЛУЧАТЕЛИ ====================


class RecipientCreateView(CreateView):
    """Создание получателя рассылки"""

    model = Recipient
    form_class = RecipientForm
    template_name = "includes/form.html"
    success_url = reverse_lazy("mailing:recipient_list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Создание получателя"
        context["cancel_url"] = reverse_lazy("mailing:recipient_list")
        return context


class RecipientUpdateView(UpdateView):
    """Редактирование получателя рассылки"""

    model = Recipient
    form_class = RecipientForm
    template_name = "includes/form.html"
    success_url = reverse_lazy("mailing:recipient_list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = f"✏️ Редактирование: {self.object.email}"
        context["cancel_url"] = reverse_lazy(
            "mailing:recipient_detail", kwargs={"pk": self.object.pk}
        )
        context["button_text"] = "Сохранить изменения"
        return context


class RecipientListView(ListView):
    """Просмотр списка получателей"""

    model = Recipient
    template_name = "mailing/recipient_list.html"
    context_object_name = "recipients"


class RecipientDetailView(DetailView):
    """Детальный просмотр получателя"""

    model = Recipient
    template_name = "mailing/recipient_detail.html"
    context_object_name = "recipient"


class RecipientDeleteView(DeleteView):
    """Удаление получателя рассылки"""

    model = Recipient
    template_name = "includes/confirm_delete.html"
    success_url = reverse_lazy("mailing:recipient_list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["cancel_url"] = reverse_lazy(
            "mailing:recipient_detail", kwargs={"pk": self.object.pk}
        )
        return context


# ==================== СООБЩЕНИЯ ====================


class MessageCreateView(CreateView):
    """Создание сообщения"""

    model = Message
    form_class = MessageForm
    template_name = "includes/form.html"
    success_url = reverse_lazy("mailing:message_list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "📝 Создание сообщения"
        context["cancel_url"] = reverse_lazy("mailing:message_list")
        context["button_text"] = "Создать сообщение"
        return context


class MessageUpdateView(UpdateView):
    """Редактирование сообщения"""

    model = Message
    form_class = MessageForm
    template_name = "includes/form.html"
    success_url = reverse_lazy("mailing:message_list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = f"✏️ Редактирование: {self.object.subject}"
        context["cancel_url"] = reverse_lazy(
            "mailing:message_detail", kwargs={"pk": self.object.pk}
        )
        context["button_text"] = "Сохранить изменения"
        return context


class MessageDeleteView(DeleteView):
    """Удаление сообщения"""

    model = Message
    template_name = "includes/confirm_delete.html"
    success_url = reverse_lazy("mailing:message_list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["cancel_url"] = reverse_lazy(
            "mailing:message_detail", kwargs={"pk": self.object.pk}
        )
        return context


class MessageListView(ListView):
    """Список сообщений"""

    model = Message
    template_name = "mailing/message_list.html"
    context_object_name = "messages"


class MessageDetailView(DetailView):
    """Детальный просмотр сообщения"""

    model = Message
    template_name = "mailing/message_detail.html"
    context_object_name = "message"


# ==================== РАССЫЛКИ ====================


class MailingCreateView(CreateView):
    """Создание рассылки"""

    model = Mailing
    form_class = MailingForm
    template_name = "includes/form.html"
    success_url = reverse_lazy("mailing:mailing_list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "📨 Создание рассылки"
        context["cancel_url"] = reverse_lazy("mailing:mailing_list")
        context["button_text"] = "Создать рассылку"
        return context


class MailingUpdateView(UpdateView):
    """Редактирование рассылки"""

    model = Mailing
    form_class = MailingForm
    template_name = "includes/form.html"
    success_url = reverse_lazy("mailing:mailing_list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = (
            f"✏️ Редактирование рассылки #{self.object.id} - {self.object.message.subject}"
        )
        context["cancel_url"] = reverse_lazy(
            "mailing:mailing_detail", kwargs={"pk": self.object.pk}
        )
        context["button_text"] = "Сохранить изменения"
        return context


class MailingDeleteView(DeleteView):
    """Удаление рассылки"""

    model = Mailing
    template_name = "includes/confirm_delete.html"
    success_url = reverse_lazy("mailing:mailing_list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["cancel_url"] = reverse_lazy(
            "mailing:mailing_detail", kwargs={"pk": self.object.pk}
        )
        return context


class MailingListView(ListView):
    """Список рассылки"""

    model = Mailing
    template_name = "mailing/mailing_list.html"
    context_object_name = "mailings"


class MailingDetailView(DetailView):
    """Детальная информация о рассылке"""

    model = Mailing
    template_name = "mailing/mailing_detail.html"
    context_object_name = "mailing"


def run_mailing(request, pk):
    """
    Функция для ручного запуска рассылки.
    Вызывается при нажатии кнопки на странице детального просмотра.
    """

    # 1. Находим рассылку по ID или выдаём 404 ошибку
    mailing = get_object_or_404(Mailing, id=pk)

    # 2. Проверяем, можно ли отправлять письма (только если статус 'launched' - текущее время между start_time и end_time)
    if mailing.get_dynamic_status() != "launched":
        messages.error(
            request,
            f'❌ Нельзя запустить рассылку со статусом "{mailing.get_status_display()}". '
            f"Отправка возможна только в период с {mailing.start_time} по {mailing.end_time}.",
        )
        return redirect("mailing:mailing_detail", pk=pk)

    # 3. Счётчики для статистики
    success_count = 0
    fail_count = 0

    # 4. Отправляем письма каждому получателю
    for recipient in mailing.recipients.all():
        try:
            # Пытаемся отправить письмо
            send_mail(
                subject=mailing.message.subject,  # Тема письма
                message=mailing.message.email_body,  # Тело письма
                from_email=settings.DEFAULT_FROM_EMAIL,  # От кого (из настроек)
                recipient_list=[recipient.email],  # Кому (список из одного email)
                fail_silently=False,  # Если ошибка — выбрасывать исключение
            )
            # Если отправка успешна
            status = "success"
            response = "✅ Письмо успешно отправлено"
            success_count += 1

        except Exception as e:
            # Если произошла ошибка — сохраняем её текст
            status = "failure"
            response = f"❌ Ошибка: {str(e)}"
            fail_count += 1

        # 5. Сохраняем запись о попытке (успешной или неудачной)
        MailingAttempt.objects.create(
            status=status,
            server_response=response,
            mailing=mailing,
            recipient=recipient,  # ← запоминаем, кому отправляли
        )

    # 6. Выводим сообщение пользователю о результате
    messages.success(
        request,
        f'📨 Рассылка "#{mailing.id}" завершена: ✅ успешно {success_count}, ❌ ошибок {fail_count}',
    )

    # 7. Возвращаемся на страницу детального просмотра рассылки
    return redirect("mailing:mailing_detail", pk=pk)


class HomeView(TemplateView):
    """Главная страница со статистикой"""

    template_name = "mailing/home.html"

    def get_context_data(self, **kwargs):
        """Этот метод собирает все данные для передачи в шаблон"""

        # Создаём словарь, в который будем складывать данные
        context = super().get_context_data(**kwargs)

        # ========== 1. ОБЩЕЕ КОЛИЧЕСТВО РАССЫЛОК ==========
        # .count() — это метод Django, который выполняет SQL запрос:
        # SELECT COUNT(*) FROM mailing_mailing;
        total_mailings = Mailing.objects.count()

        # ========== 2. КОЛИЧЕСТВО АКТИВНЫХ РАССЫЛОК ==========
        # Активная рассылка — это та, у которой:
        #   - start_time <= текущее время (уже началась)
        #   - end_time >= текущее время (ещё не закончилась)

        # Получаем текущее время с учётом часового пояса
        now = timezone.now()

        # filter() находит все рассылки, которые подходят под условия
        # start_time__lte=now  → start_time <= now (lte = Less Than or Equal)
        # end_time__gte=now    → end_time >= now (gte = Greater Than or Equal)
        active_mailings = Mailing.objects.filter(
            start_time__lte=now,  # рассылка уже началась
            end_time__gte=now,  # рассылка ещё не закончилась
        ).count()

        # ========== 3. КОЛИЧЕСТВО УНИКАЛЬНЫХ ПОЛУЧАТЕЛЕЙ ==========
        # Просто считаем всех клиентов в таблице Recipient
        unique_recipients = Recipient.objects.count()

        # ========== 4. КЛАДЁМ ДАННЫЕ В КОНТЕКСТ ==========
        # Всё, что мы положим в context, будет доступно в шаблоне
        context["total_mailings"] = total_mailings
        context["active_mailings"] = active_mailings
        context["unique_recipients"] = unique_recipients

        # Возвращаем словарь с данными
        return context
