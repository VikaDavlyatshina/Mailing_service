from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

# Create your models here.


class Recipient(models.Model):
    """Модель получателя рассылки"""

    email = models.EmailField(
        unique=True, verbose_name="Email", help_text="Введите email получателя"
    )
    full_name = models.CharField(
        max_length=250,
        verbose_name="Ф.И.О. получателя",
        help_text="Введите Ф.И.О. получателя рассылки",
    )
    comment = models.TextField(
        blank=True,
        verbose_name="Комментарий",
        help_text="Укажите комментарий для получателя",
    )

    def __str__(self):
        return self.email

    class Meta:
        verbose_name = "Получатель рассылки"
        verbose_name_plural = "Получатели рассылки"
        ordering = ["email"]


class Message(models.Model):
    """Модель сообщения"""

    # Тема письма
    subject = models.CharField(
        max_length=150, verbose_name="Тема письма", help_text="Укажите тему письма"
    )
    # Тело письма
    email_body = models.TextField()

    # Показываем тему письма
    def __str__(self):
        return self.subject

    class Meta:
        verbose_name = "Сообщение"
        verbose_name_plural = "Сообщения"


class Mailing(models.Model):
    """Модель рассылки"""

    # Статусы рассылки
    STATUS_CHOICES = [
        ("created", "Создана"),
        ("launched", "Запущена"),
        ("completed", "Завершена"),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="created")

    # У одной рассылки может быть много получателей
    recipients = models.ManyToManyField(
        Recipient,
        verbose_name="Получатели",
        related_name="mailings",
    )
    # К рассылке привязано сообщение
    # При удалении сообщения - удаляются все связанные рассылки
    message = models.ForeignKey(
        Message,
        on_delete=models.CASCADE,
        verbose_name="Сообщение",
        related_name="mailings",
    )

    # Дата и время начала отправки
    start_time = models.DateTimeField(verbose_name="Дата и время начала рассылки")
    # До какого момента разрешено отправлять рассылку
    end_time = models.DateTimeField(verbose_name="Дата и время окончания рассылки")

    def clean(self):
        """Валидация - вызывается перед сохранением"""
        if self.start_time and self.end_time:
            if self.start_time >= self.end_time:
                raise ValidationError("Дата начала должна быть раньше даты окончания")

        # Проверяем новые рассылки
        if not self.pk and self.start_time and self.start_time < timezone.now():
            raise ValidationError("Нельзя создать рассылку в прошлом")

    def get_dynamic_status(self):
        """Вычисляет статус по датам"""
        now = timezone.now()

        # Если сейчас раньше, чем начало отправки - статус Создана
        if now < self.start_time:
            return "created"
        # Если сейчас позже, чем начало отправки, но раньше окончания - статус Запущена
        elif self.start_time <= now <= self.end_time:
            return "launched"
        else:
            return "completed"

    def update_status(self):
        """Обновляет статус в БД, если он изменился"""

        # 1. Вычисляем правильный статус на основе текущего времени
        new_status = self.get_dynamic_status()

        # 2. Сравниваем с тем, что хранится в БД
        if self.status != new_status:
            # 3. Если статус отличается - обновляем
            self.status = new_status
            self.save(update_fields=["status"])  # сохраняем только статус

    def save(self, *args, **kwargs):
        """Сохранение статуса с валидацией времени и автообновлением статуса"""

        # Проверяем даты
        self.clean()
        # Обновляем статус
        self.status = self.get_dynamic_status()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Рассылка #{self.id} - {self.message.subject}"

    class Meta:
        verbose_name = "Рассылка"
        verbose_name_plural = "Рассылки"
        ordering = ["-start_time"]  # сначала новые рассылки


class MailingAttempt(models.Model):
    """Модель попытки рассылок"""

    STATUS_CHOICES = [("success", "Успешно"), ("failure", "Не успешно")]

    attempt_time = models.DateTimeField(
        auto_now_add=True, verbose_name="Дата и время попытки"
    )
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, verbose_name="Статус попытки отправки"
    )
    server_response = models.TextField(
        verbose_name="Ответ почтового сервера", blank=True
    )
    mailing = models.ForeignKey(
        Mailing,
        on_delete=models.CASCADE,
        related_name="attempts",
        verbose_name="Рассылка",
    )

    # Получатель - чтобы знать, кому не отправилась рассылка
    recipient = models.ForeignKey(
        Recipient,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name="Получатель",
    )

    def __str__(self):
        return f"Попытка от {self.attempt_time} - {self.status}"

    class Meta:
        verbose_name = "Попытка рассылки"
        verbose_name_plural = "Попытки рассылок"
        ordering = ["-attempt_time"]
