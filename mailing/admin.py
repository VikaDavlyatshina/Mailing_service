from django.contrib import admin
from mailing.models import Mailing, Recipient, Message, MailingAttempt


# Register your models here.

@admin.register(Recipient)
class RecipientAdmin(admin.ModelAdmin):
    """ Настройка отображения Получателей в админке """

    # Поля, которые отображаются в списке
    list_display = ( 'email', 'full_name', 'comment_preview', 'owner')

    # Поля, по которым можно фильтровать
    list_filter = ('owner', 'full_name')

    # Поля, по которым можно искать

    # Двойное подчеркивание __ для того, чтобы взять связанное значение из другой таблицы
    # owner__email - искать по email владельца
    search_fields = ('owner__email', 'full_name', 'email')

    # Сортировка по умолчанию
    ordering = ['email']

    def comment_preview(self, obj):
        """Показывает первые 30 символов комментария."""
        # Проверяем, есть ли комментарий
        if obj.comment:
            # Если длина больше 30 — обрезаем и добавляем '...'
            if len(obj.comment) > 30:
                return obj.comment[:30] + '...'
            # Если короче — возвращаем как есть
            return obj.comment
        # Если комментария нет — возвращаем прочерк
        return "—"

    # Это нужно, чтобы в таблице был нормальный заголовок колонки
    comment_preview.short_description = 'Комментарий'


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    """ Настройка отображения Сообщения в админке """

    # Поля, которые отображаются в списке
    list_display = ('subject', 'body_preview', 'owner')

    # Поля, по которым можно фильтровать
    list_filter = ('owner', 'subject')

    # Поля, по которым можно искать
    search_fields = ('owner', 'subject', 'email_body')

    # Сортировка по умолчанию
    ordering = ['subject']

    def body_preview(self, obj):
        """Показывает первые 50 символов тела сообщения."""
        if obj.email_body:
            if len(obj.email_body) > 50:
                return obj.email_body[:50] + '...'
            return obj.email_body
        return "—"

    body_preview.short_description = 'Текст сообщения'


@admin.register(Mailing)
class MailingAdmin(admin.ModelAdmin):
    """ Настройка отображения Рассылки в админке """

    # Поля, которые отображаются в списке
    list_display = ('status','message_subject', 'recipients_count', 'start_time', 'end_time', 'owner')

    # # Поля, которые отображаются в списке
    # list_display = ('status', 'recipients', 'message', 'start_time', 'end_time', 'owner')

    # Поля, по которым можно фильтровать
    list_filter = ('owner', 'status', 'start_time', 'end_time')

    # Поля, по которым можно искать
    search_fields = ('owner__email', 'message__subject', 'status')

    # Сортировка по умолчанию
    ordering = ['-start_time']  # Минус = по убыванию (новые сверху)

    def message_subject(self, obj):
        """Возвращает тему сообщения, привязанного к рассылке."""
        # obj.message — это объект Message
        # obj.message.subject — его тема
        return obj.message.subject

    message_subject.short_description = 'Тема сообщения'

    def recipients_count(self, obj):
        """Возвращает количество получателей в рассылке."""
        # obj.recipients — это менеджер ManyToMany
        # .count() возвращает количество записей
        return obj.recipients.count()

    recipients_count.short_description = 'Получателей'



@admin.register(MailingAttempt)
class MailingAttemptAdmin(admin.ModelAdmin):
    """ Настройка отображения Попытки рассылки в админке """

    def has_add_permission(self, request):
        """Запрещает создание новых попыток через админку."""
        return False

    def has_change_permission(self, request, obj=None):
        """Запрещает редактирование попыток."""
        return False

    # Поля, которые отображаются в списке
    list_display = ('attempt_time', 'status', 'server_response', 'mailing', 'recipient')
    readonly_fields = ['attempt_time', 'status', 'server_response', 'mailing', 'recipient']

    # Поля, по которым можно фильтровать
    list_filter = ('status', 'mailing')

    # Поля, по которым можно искать
    search_fields = ('status', 'mailing')

    # Сортировка по умолчанию
    ordering = ['status']


