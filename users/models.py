from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.text import slugify
from phonenumber_field.modelfields import PhoneNumberField


# Create your models here.
class CustomUserManager(BaseUserManager):
    """Менеджер для кастомной модели пользователя."""

    def create_user(self, email, password=None, **extra_fields):
        """
        Создание обычного пользователя.
        """
        # Проверяем, что email указан
        if not email:
            raise ValueError('Email обязателен')

        # Приводим email к нижнему регистру
        email = self.normalize_email(email)

        # Если username не передан — создаёт из email
        if 'username' not in extra_fields or not extra_fields.get('username'):
            extra_fields['username'] = email.split('@')[0]

        # Создаём объект пользователя
        user = self.model(email=email, **extra_fields)
        # Хэшируем пароль
        user.set_password(password)
        # Сохраняем в БД
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """
        Создание суперпользователя.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if not extra_fields.get('is_staff'):
            raise ValueError('Суперпользователь должен иметь is_staff=True')
        if not extra_fields.get('is_superuser'):
            raise ValueError('Суперпользователь должен иметь is_superuser=True')

        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractUser):
    """
    Кастомная модель пользователя.
    Вход осуществляется по email. Username опционален, но уникален.
    """

    # 1. Username — уникальный, но может быть пустым
    username = models.CharField(
        max_length=150,
        unique=True,
        blank=True,
        null=True,
        verbose_name="Логин (опционально)" ,
        help_text="Будет создан автоматически из email, если не указан"
    )
    # 2. Slug для красивых URL (автоматически из username)
    slug = models.SlugField(
        max_length=150,
        unique=True,
        blank=True,
        null=True,
        verbose_name="Slug для URL",
        help_text="Автоматически создаётся из username"
    )

    # 3. Основной идентификатор для входа
    email = models.EmailField(
        unique=True,
        verbose_name="Email",
        help_text="Используется для входа в систему"
    )

    # 4. Дополнительные поля
    phone = PhoneNumberField(verbose_name="Телефон", help_text="Введите номер телефона", blank=True, null=True, )
    avatar = models.ImageField(
        upload_to="users/avatars/", verbose_name="Аватар", help_text="Загрузите свой аватар", blank=True, null=True, )
    birth_date = models.DateField(verbose_name='Дата рождения', help_text='Укажите дату рождения', blank=True,
                                  null=True)
    # Токен для подтверждения email (очищается после подтверждения)
    token = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Токен подтверждения",
        help_text="Используется для верификации email при регистрации"
    )
    # 5. Кастомный менеджер
    objects = CustomUserManager()

    # 6. Настройки аутентификации

    # Указываем, что для входа используется email
    USERNAME_FIELD = "email"
    # Поля, которые запрашиваются при создании createsuperuser (кроме email и пароля)
    REQUIRED_FIELDS = ["first_name", "last_name"]

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
        ordering = ['username']  # Сортировка по username

    def save(self, *args, **kwargs):
        """Автоматически создаём username и slug, если они пустые"""
        if not self.username and self.email:
            base_username = self.email.split('@')[0]
            self.username = base_username

            # Проверяем уникальность с ограничением
            counter = 1
            max_attempts = 100  # Защита от бесконечного цикла
            while CustomUser.objects.filter(username=self.username).exists() and counter <= max_attempts:
                self.username = f"{base_username}{counter}"
                counter += 1

        # Создаём slug из username
        if self.username and not self.slug:
            self.slug = slugify(self.username)

        super().save(*args, **kwargs)

    def __str__(self):
        return self.username if self.username else self.email

    def get_display_name(self):
        """Имя для отображения в интерфейсе"""
        if self.username:
            return self.username
        if self.first_name:
            return self.first_name
        return self.email.split('@')[0]

    def get_absolute_url(self):
        """URL для профиля пользователя"""
        from django.urls import reverse
        if self.slug:
            return reverse('users:profile', kwargs={'slug': self.slug})
        return reverse('users:profile', kwargs={'pk': self.pk})