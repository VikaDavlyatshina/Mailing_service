from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission


class Command(BaseCommand):
    help = 'Создаёт группу "Менеджеры" с правами'

    def handle(self, *args, **options):
        # Создаём группу
        group, created = Group.objects.get_or_create(name='Менеджеры')

        # Список нужных прав
        permissions_codenames = [
            "can_view_all_recipients",
            "can_view_all_messages",
            "can_view_all_mailings",
            "can_disable_mailings",
        ]

        # Назначаем права
        for codename in permissions_codenames:
            try:
                perm = Permission.objects.get(codename=codename)
                group.permissions.add(perm)
                self.stdout.write(f" - Добавлено разрешение {codename}")
            except Permission.DoesNotExist:
                self.stdout.write(self.style.WARNING(f'  - Разрешение {codename} не найдено'))

        self.stdout.write(self.style.SUCCESS('✅ Группа "Менеджеры" настроена'))

        if created:
            self.stdout.write(self.style.SUCCESS('✅ Группа "Менеджеры" создана'))
        else:
            self.stdout.write('Группа "Менеджеры" уже существует')