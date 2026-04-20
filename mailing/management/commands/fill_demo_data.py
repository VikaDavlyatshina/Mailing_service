from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from mailing.models import Recipient, Message, Mailing
from django.utils import timezone
from datetime import timedelta

User = get_user_model()


class Command(BaseCommand):
    help = 'Заполняет базу данных демонстрационными данными'

    def handle(self, *args, **options):
        self.stdout.write('=' * 60)
        self.stdout.write('ЗАПОЛНЕНИЕ БАЗЫ ДАННЫХ ДЕМО-ДАННЫМИ')
        self.stdout.write('=' * 60)

        # 1. Группа "Менеджеры"
        self.stdout.write('\n[1] СОЗДАНИЕ ГРУППЫ "МЕНЕДЖЕРЫ"')
        group, created = Group.objects.get_or_create(name='Менеджеры')
        self.stdout.write(f'   Группа "Менеджеры" {"создана" if created else "уже существует"}')

        # 2. Пользователи
        self.stdout.write('\n[2] СОЗДАНИЕ ПОЛЬЗОВАТЕЛЕЙ')

        admin, created = User.objects.get_or_create(
            email='admin@example.com',
            defaults={
                'username': 'admin',
                'first_name': 'Администратор',
                'is_staff': True,
                'is_superuser': True
            }
        )
        if created:
            admin.set_password('admin123')
            admin.save()
        self.stdout.write(f'   Админ: admin@example.com / admin123')

        manager, created = User.objects.get_or_create(
            email='manager@example.com',
            defaults={'username': 'manager', 'first_name': 'Иван', 'last_name': 'Менеджеров'}
        )
        if created:
            manager.set_password('manager123')
            manager.save()
            manager.groups.add(group)
        self.stdout.write(f'   Менеджер: manager@example.com / manager123')

        user1, created = User.objects.get_or_create(
            email='user1@example.com',
            defaults={'username': 'user1', 'first_name': 'Анна', 'last_name': 'Иванова'}
        )
        if created:
            user1.set_password('user123')
            user1.save()
        self.stdout.write(f'   Пользователь 1: user1@example.com / user123')

        user2, created = User.objects.get_or_create(
            email='user2@example.com',
            defaults={'username': 'user2', 'first_name': 'Петр', 'last_name': 'Петров'}
        )
        if created:
            user2.set_password('user123')
            user2.save()
        self.stdout.write(f'   Пользователь 2: user2@example.com / user123')

        # 3. Получатели
        self.stdout.write('\n[3] СОЗДАНИЕ ПОЛУЧАТЕЛЕЙ')
        recipients_data = [
            {'email': 'ivanov@mail.ru', 'full_name': 'Иванов Иван', 'comment': 'VIP клиент', 'owner': user1},
            {'email': 'petrova@mail.ru', 'full_name': 'Петрова Мария', 'comment': 'Постоянный клиент', 'owner': user1},
            {'email': 'sidorov@mail.ru', 'full_name': 'Сидоров Алексей', 'comment': 'Новый клиент', 'owner': user2},
            {'email': 'smirnova@mail.ru', 'full_name': 'Смирнова Елена', 'comment': 'Тестовый клиент', 'owner': user2},
            {'email': 'kozlov@mail.ru', 'full_name': 'Козлов Дмитрий', 'comment': 'Потенциальный клиент',
             'owner': user1},
        ]
        recipients = []
        for data in recipients_data:
            r, created = Recipient.objects.get_or_create(
                email=data['email'],
                defaults={'full_name': data['full_name'], 'comment': data['comment'], 'owner': data['owner']}
            )
            recipients.append(r)
            self.stdout.write(f'   {r.email}')

        # 4. Сообщения
        self.stdout.write('\n[4] СОЗДАНИЕ СООБЩЕНИЙ')
        messages_data = [
            {'subject': 'Специальное предложение!', 'email_body': 'Скидка 30% на все товары!', 'owner': user1},
            {'subject': 'Новое поступление', 'email_body': 'Новая коллекция осень-зима.', 'owner': user1},
            {'subject': 'Персональная скидка', 'email_body': 'Промокод SALE20 на скидку 20%.', 'owner': user2},
            {'subject': 'Бесплатная доставка', 'email_body': 'Доставка бесплатно от 3000 рублей.', 'owner': user2},
        ]
        messages = []
        for data in messages_data:
            m, created = Message.objects.get_or_create(
                subject=data['subject'],
                defaults={'email_body': data['email_body'], 'owner': data['owner']}
            )
            messages.append(m)
            self.stdout.write(f'   {m.subject}')

        # 5. Рассылки (ВСЕ ДАТЫ В БУДУЩЕМ ОТНОСИТЕЛЬНО МОМЕНТА ЗАПУСКА)
        self.stdout.write('\n[5] СОЗДАНИЕ РАССЫЛОК')
        now = timezone.now()

        mailings_data = [
            {
                'message': messages[0],
                'start': now + timedelta(minutes=5),
                'end': now + timedelta(days=7),
                'recipients': [recipients[0], recipients[1]],
                'owner': user1,
                'status': 'created'
            },
            {
                'message': messages[1],
                'start': now + timedelta(minutes=10),
                'end': now + timedelta(days=8),
                'recipients': [recipients[2]],
                'owner': user2,
                'status': 'created'
            },
            {
                'message': messages[2],
                'start': now + timedelta(minutes=15),
                'end': now + timedelta(days=9),
                'recipients': [recipients[3]],
                'owner': user2,
                'status': 'created'
            },
            {
                'message': messages[3],
                'start': now + timedelta(minutes=20),
                'end': now + timedelta(days=10),
                'recipients': [recipients[4]],
                'owner': user1,
                'status': 'created'
            },
        ]

        for data in mailings_data:
            # Проверяем, существует ли уже такая рассылка
            existing_mailing = Mailing.objects.filter(
                message=data['message'],
                start_time=data['start'],
                end_time=data['end']
            ).first()

            if existing_mailing:
                self.stdout.write(
                    f'   Рассылка #{existing_mailing.id} - {existing_mailing.message.subject} (уже существует)')
                continue

            mailing = Mailing(
                message=data['message'],
                start_time=data['start'],
                end_time=data['end'],
                owner=data['owner'],
                status=data['status']
            )
            mailing.save()
            mailing.recipients.set(data['recipients'])
            mailing.save()
            self.stdout.write(f'   Рассылка #{mailing.id} - {mailing.message.subject} (создана)')

        # 6. Права группы
        self.stdout.write('\n[6] НАСТРОЙКА ПРАВ ГРУППЫ "МЕНЕДЖЕРЫ"')
        permissions = Permission.objects.filter(codename__in=[
            'can_view_all_recipients',
            'can_view_all_mailings',
            'can_disable_mailings'
        ])
        for perm in permissions:
            group.permissions.add(perm)
        self.stdout.write(f'   Добавлено {permissions.count()} прав группе')

        # Итог
        self.stdout.write('\n' + '=' * 60)
        self.stdout.write('ГОТОВО! БАЗА ДАННЫХ ЗАПОЛНЕНА')
        self.stdout.write('=' * 60)
        self.stdout.write('\nДАННЫЕ ДЛЯ ВХОДА:')
        self.stdout.write('   Администратор: admin@example.com / admin123')
        self.stdout.write('   Менеджер: manager@example.com / manager123')
        self.stdout.write('   Пользователь 1: user1@example.com / user123')
        self.stdout.write('   Пользователь 2: user2@example.com / user123')