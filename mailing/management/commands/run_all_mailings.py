"""
Кастомная команда для автоматического запуска ВСЕХ активных рассылок.
Запуск: python manage.py run_all_mailings
"""

from django.conf import settings
from django.core.mail import send_mail
from django.core.management.base import BaseCommand
from django.utils import timezone

from mailing.models import Mailing, MailingAttempt


class Command(BaseCommand):
    """
    Команда для автоматического запуска всех активных рассылок.

    Использование:
        python manage.py run_all_mailings

    Что делает:
        1. Находит все рассылки со статусом 'launched'
        2. Для каждой отправляет письма всем получателям
        3. Сохраняет попытки в MailingAttempt
        4. Выводит общую статистику
    """

    help = "Автоматически запускает ВСЕ активные рассылки"

    def handle(self, *args, **options):

        # 1. Получаем текущее время
        now = timezone.now()

        # 2. Находим все активные рассылки
        active_mailings = Mailing.objects.filter(
            status="launched",
            start_time__lte=now,  # Уже началась
            end_time__gte=now,  # Ещё не закончилась
        )

        # 3. Если активных рассылок нет
        if not active_mailings.exists():
            self.stdout.write(
                self.style.WARNING("⚠️ Нет активных рассылок для отправки.")
            )
            return

        # 4. Счётчики для общей статистики
        total_mailings = active_mailings.count()
        total_success = 0
        total_fail = 0

        self.stdout.write(
            self.style.SUCCESS(f"\n📨 Найдено активных рассылок: {total_mailings}")
        )
        self.stdout.write("=" * 60)

        # 5. Обрабатываем каждую рассылку
        for mailing in active_mailings:
            self.stdout.write(
                f'\n📧 Рассылка #{mailing.id}: "{mailing.message.subject}"'
            )

            success_count = 0
            fail_count = 0

            # 6. Отправляем письма всем получателям
            for recipient in mailing.recipients.all():
                try:
                    send_mail(
                        subject=mailing.message.subject,
                        message=mailing.message.email_body,
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[recipient.email],
                        fail_silently=False,
                    )

                    status = "success"
                    response = "✅ Письмо успешно отправлено"
                    success_count += 1
                    total_success += 1

                except Exception as e:
                    status = "failure"
                    response = f"❌ Ошибка: {str(e)}"
                    fail_count += 1
                    total_fail += 1

                # 7. Сохраняем попытку
                MailingAttempt.objects.create(
                    status=status,
                    server_response=response,
                    mailing=mailing,
                    recipient=recipient,
                )

            # 8. Статистика по текущей рассылке
            self.stdout.write(
                f"   ✅ Успешно: {success_count}  ❌ Ошибок: {fail_count}"
            )

        # 9. Итоговая статистика
        self.stdout.write("\n" + "=" * 60)
        self.stdout.write(
            self.style.SUCCESS(
                f"🎯 ВСЕГО ОТПРАВЛЕНО: ✅ {total_success} успешно, ❌ {total_fail} ошибок"
            )
        )
