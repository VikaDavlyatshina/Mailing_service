from django.conf import settings
from django.core.mail import send_mail
from django.core.management.base import BaseCommand

from mailing.models import Mailing, MailingAttempt


class Command(BaseCommand):
    help = "Запускает рассылку по ID из командной строки"

    def add_arguments(self, parser):
        """Добавляем аргумент — ID рассылки"""
        parser.add_argument("mailing_id", type=int, help="ID рассылки для запуска")

    def handle(self, *args, **options):
        """Основная логика команды"""
        mailing_id = options["mailing_id"]

        # 1. Находим рассылку
        try:
            mailing = Mailing.objects.get(id=mailing_id)
        except Mailing.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f"❌ Рассылка с ID {mailing_id} не найдена")
            )
            return

        # 2. Проверяем статус
        if mailing.get_dynamic_status() != "launched":
            self.stdout.write(
                self.style.ERROR(
                    f'❌ Нельзя запустить рассылку со статусом "{mailing.get_status_display()}"'
                )
            )
            return

        # 3. Отправляем письма
        success_count = 0
        fail_count = 0

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

            except Exception as e:
                status = "failure"
                response = f"❌ Ошибка: {str(e)}"
                fail_count += 1

            MailingAttempt.objects.create(
                status=status,
                server_response=response,
                mailing=mailing,
                recipient=recipient,
            )

        # 4. Выводим результат
        self.stdout.write(
            self.style.SUCCESS(
                f"📨 Рассылка #{mailing_id} завершена: ✅ {success_count}, ❌ {fail_count}"
            )
        )
