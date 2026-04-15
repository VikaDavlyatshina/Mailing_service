from django.contrib import admin
from django.utils.safestring import mark_safe  # <-- Вместо format_html
from mailing.models import Mailing, Recipient, Message, MailingAttempt


@admin.register(Recipient)
class RecipientAdmin(admin.ModelAdmin):
    """Настройка отображения Получателей в админке."""

    # Поля, которые отображаются в списке
    list_display = ('id', 'email', 'full_name', 'comment_preview', 'owner')

    # Поля, по которым можно фильтровать
    list_filter = ('owner',)

    # Сколько записей на странице
    list_per_page = 20

    # Поля, по которым можно искать
    search_fields = ('owner__email', 'full_name', 'email')

    # Сортировка по умолчанию
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
    """Настройка отображения Сообщений в админке."""

    # Поля, которые отображаются в списке
    list_display = ('id', 'subject', 'body_preview', 'owner')

    # Сколько записей на странице
    list_per_page = 20

    # Поля, по которым можно фильтровать
    list_filter = ('owner',)

    # Поля, которые можно редактировать прямо в списке
    # (двойное подчёркивание = переход к связанной модели)
    search_fields = ('owner__email', 'subject', 'email_body')

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
    """
    Настройка отображения Рассылок в админке.

    Особенности:
    - Статус отображается цветной плашкой
    - Показывается количество получателей
    - Сортировка по дате начала (новые сверху)
    """

    # Поля, которые видит пользователь в таблице
    list_display = (
        'id',
        'message_subject',  # Тема письма
        'recipients_count',  # Количество получателей
        'status_badge',  # Цветной статус
        'start_time',  # Дата начала
        'end_time',  # Дата окончания
        'owner',  # Владелец
    )

    # Фильтры в правой колонке
    list_filter = ('status', 'owner', 'start_time')

    # Сколько записей на странице
    list_per_page = 20

    # Поля для поиска (двойное подчёркивание = переход к связанной модели)
    search_fields = ('owner__email', 'message__subject')

    # Сортировка по умолчанию (минус = по убыванию)
    ordering = ['-start_time']

    # ========== КАСТОМНЫЕ МЕТОДЫ ДЛЯ ОТОБРАЖЕНИЯ ==========

    def status_badge(self, obj):
        """
        Отображает статус в виде цветной плашки.
        Использует mark_safe для безопасной вставки HTML.
        """
        # Определяем цвет и текст для каждого статуса
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
            color = '#999999'  # Светло-серый
            text = obj.status

        # Создаём HTML-код плашки через f-строку
        html = f'''
            <span style="
                background-color: {color};
                color: white;
                padding: 4px 8px;
                border-radius: 4px;
                font-weight: 500;
                font-size: 13px;
            ">{text}</span>
        '''
        # mark_safe говорит Django: "Этот HTML безопасен, отобрази его"
        return mark_safe(html)

    status_badge.short_description = 'Статус'
    status_badge.admin_order_field = 'status'  # Разрешаем сортировку по статусу

    def message_subject(self, obj):
        """Возвращает тему сообщения, привязанного к рассылке."""
        return obj.message.subject

    message_subject.short_description = 'Тема письма'
    message_subject.admin_order_field = 'message__subject'

    def recipients_count(self, obj):
        """Возвращает количество получателей в рассылке."""
        return obj.recipients.count()

    recipients_count.short_description = 'Кол-во получателей'


@admin.register(MailingAttempt)
class MailingAttemptAdmin(admin.ModelAdmin):
    """
    Настройка отображения Попыток рассылки.

    Особенности:
    - Нельзя создавать и редактировать попытки (только просмотр)
    - Статус отображается цветной плашкой
    - Длинные ответы сервера обрезаются
    """

    # Поля в таблице
    list_display = (
        'id',
        'attempt_time',  # Время попытки
        'mailing',  # Ссылка на рассылку
        'recipient',  # Получатель
        'response_preview',  # Превью ответа сервера
        'status_badge',  # Цветной статус
    )

    # Сколько записей на странице
    list_per_page = 20

    # Фильтры
    list_filter = ('status', 'mailing')

    # Поиск
    search_fields = ('mailing__message__subject', 'recipient__email', 'server_response')

    # Сортировка (новые сверху)
    ordering = ['-attempt_time']

    # Все поля только для чтения
    readonly_fields = ('attempt_time', 'status', 'server_response', 'mailing', 'recipient')

    # ========== ЗАПРЕТ НА ИЗМЕНЕНИЕ ==========

    def has_add_permission(self, request):
        """Запрещает создание новых попыток через админку."""
        return False

    def has_change_permission(self, request, obj=None):
        """Запрещает редактирование существующих попыток."""
        return False

    # ========== КАСТОМНЫЕ МЕТОДЫ ДЛЯ ОТОБРАЖЕНИЯ ==========

    def status_badge(self, obj):
        """Отображает статус попытки в виде цветной плашки."""
        if obj.status == 'success':
            color = '#28a745'  # Зелёный = успех
            text = 'Успешно'
        else:
            color = '#dc3545'  # Красный = ошибка
            text = 'Ошибка'

        html = f'''
            <span style="
                background-color: {color};
                color: white;
                padding: 4px 8px;
                border-radius: 4px;
                font-weight: 500;
                font-size: 13px;
            ">{text}</span>
        '''
        return mark_safe(html)

    status_badge.short_description = 'Статус'
    status_badge.admin_order_field = 'status'

    def response_preview(self, obj):
        """Показывает первые 50 символов ответа сервера."""
        if obj.server_response:
            if len(obj.server_response) > 50:
                return obj.server_response[:50] + '...'
            return obj.server_response
        return "—"

    response_preview.short_description = 'Ответ сервера'
