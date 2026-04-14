from django.contrib import admin
from django.utils.html import format_html  # <-- ВАЖНО! Импортируем для HTML
from mailing.models import Mailing, Recipient, Message, MailingAttempt


@admin.register(Recipient)
class RecipientAdmin(admin.ModelAdmin):
    """Настройка отображения Получателей в админке"""

    list_display = ('id', 'email', 'full_name', 'comment_preview', 'owner')
    list_filter = ('owner',)
    search_fields = ('owner__email', 'full_name', 'email')
    ordering = ['email']

    def comment_preview(self, obj):
        """Показывает первые 30 символов комментария."""
        if obj.comment:
            if len(obj.comment) > 30:
                return obj.comment[:30] + '...'
            return obj.comment
        return "—"

    comment_preview.short_description = 'Комментарий'


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    """Настройка отображения Сообщений в админке"""

    list_display = ('id', 'owner', 'subject', 'body_preview')
    list_filter = ('owner',)
    search_fields = ('owner__email', 'subject', 'email_body')
    ordering = ['subject']

    def body_preview(self, obj):
        """Показывает первые 50 символов тела сообщения."""
        if obj.email_body:
            if len(obj.email_body) > 50:
                return obj.email_body[:50] + '...'
            return obj.email_body
        return "—"

    body_preview.short_description = 'Текст'


@admin.register(Mailing)
class MailingAdmin(admin.ModelAdmin):
    """Настройка отображения Рассылок в админке"""

    # Поля в таблице
    list_display = (
        'id',
        'message_subject',
        'recipients_count',
        'start_time',
        'end_time',
        'status_badge',
        'owner',
    )

    # Фильтры справа
    list_filter = ('status', 'owner', 'start_time')

    # Поиск
    search_fields = ('owner__email', 'message__subject')

    # Сортировка (новые сверху)
    ordering = ['-start_time']

    # ========== КАСТОМНЫЕ ПОЛЯ ==========

    def status_badge(self, obj):
        """Красивая цветная плашка для статуса (как Bootstrap badge)."""

        # Настройки для каждого статуса
        if obj.status == 'created':
            color = '#6c757d'  # Серый
            text = 'Создана'
        elif obj.status == 'launched':
            color = '#28a745'  # Зелёный
            text = 'Запущена'
        elif obj.status == 'completed':
            color = '#007bff'  # Синий
            text = 'Завершена'
        else:
            color = '#999999'
            text = obj.status

        # Создаём HTML-плашку
        return format_html(
            '<span style="background-color: {}; color: white; '
            'padding: 4px 8px; border-radius: 4px; '
            'font-weight: 500; font-size: 13px;">{}</span>',
            color, text
        )

    status_badge.short_description = 'Статус'
    status_badge.admin_order_field = 'status'  # Можно сортировать по статусу

    def message_subject(self, obj):
        """Показывает тему сообщения."""
        return obj.message.subject

    message_subject.short_description = 'Тема'
    message_subject.admin_order_field = 'message__subject'

    def recipients_count(self, obj):
        """Показывает количество получателей."""
        return obj.recipients.count()

    recipients_count.short_description = 'Получателей'


@admin.register(MailingAttempt)
class MailingAttemptAdmin(admin.ModelAdmin):
    """Настройка отображения Попыток рассылки"""

    list_display = ('attempt_time', 'mailing', 'recipient', 'status_badge', 'response_preview')
    list_filter = ('status', 'mailing')
    search_fields = ('mailing__message__subject', 'recipient__email', 'server_response')
    ordering = ['-attempt_time']

    # Только для чтения
    readonly_fields = ('attempt_time', 'status', 'server_response', 'mailing', 'recipient')

    # Запрещаем создание и редактирование
    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    # ========== КАСТОМНЫЕ ПОЛЯ ==========

    def status_badge(self, obj):
        """Цветная плашка для статуса попытки."""
        if obj.status == 'success':
            color = '#28a745'
            text = 'Успешно'
        else:
            color = '#dc3545'
            text = 'Ошибка'

        return format_html(
            '<span style="background-color: {}; color: white; '
            'padding: 4px 8px; border-radius: 4px; '
            'font-weight: 500; font-size: 13px;">{}</span>',
            color, text
        )

    status_badge.short_description = 'Статус'

    def response_preview(self, obj):
        """Показывает первые 50 символов ответа сервера."""
        if obj.server_response:
            if len(obj.server_response) > 50:
                return obj.server_response[:50] + '...'
            return obj.server_response
        return "—"

    response_preview.short_description = 'Ответ сервера'
