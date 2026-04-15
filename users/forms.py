from django import forms
from django.contrib.auth.forms import (
    AuthenticationForm,
    UserCreationForm,
    PasswordResetForm,
    SetPasswordForm,
)
from mailing.forms import BootstrapFormMixin
from users.models import CustomUser


class UserRegisterForm(BootstrapFormMixin, UserCreationForm):
    """Форма регистрации пользователя"""

    class Meta:
        model = CustomUser
        fields = ("email", "password1", "password2")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Добавляем placeholder для email
        self.fields["email"].widget.attrs["placeholder"] = "ваш@email.com"

        # Переименовываем стандартные метки полей Django
        self.fields["email"].label = "Email адрес"
        self.fields["password1"].label = "Пароль"
        self.fields["password2"].label = "Подтверждение пароля"

        # Убираем стандартные подсказки Django
        self.fields["password1"].help_text = None
        self.fields["password2"].help_text = None


class UserLoginForm(BootstrapFormMixin, AuthenticationForm):
    """Форма для входа в систему"""

    class Meta:
        model = CustomUser
        fields = ("email", "password")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Переименовываем поле username в email (так как переопределили поле входа)
        self.fields["username"].label = "Email"
        self.fields["username"].widget.attrs["placeholder"] = "ваш@email.com"
        self.fields["password"].widget.attrs["placeholder"] = "Пароль"

        # Убираем подсказку
        self.fields["username"].help_text = None


class UserProfileForm(BootstrapFormMixin, forms.ModelForm):
    """Форма редактирования профиля"""

    class Meta:
        model = CustomUser
        fields = ["phone", "avatar", "username", "first_name", "last_name"]

        labels = {
            "first_name": "Имя",
            "last_name": "Фамилия",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Добавляем placeholder-ы
        self.fields["phone"].widget.attrs["placeholder"] = "+7 (999) 123-45-67"
        self.fields["username"].widget.attrs[
            "placeholder"
        ] = "Укажите логин (опционально)"
        self.fields["first_name"].widget.attrs["placeholder"] = "Ваше имя"
        self.fields["last_name"].widget.attrs["placeholder"] = "Ваша фамилия"

        # Делаем поля необязательными
        self.fields["phone"].required = False
        self.fields["username"].required = False
        self.fields["avatar"].required = False
        self.fields["first_name"].required = False
        self.fields["last_name"].required = False

        # Убираем английские подсказки у аватара
        self.fields["avatar"].help_text = "Загрузите изображение (jpg, png, webp)"

        # Кастомный текст для кнопок аватара
        avatar_field = self.fields.get("avatar")
        if avatar_field and hasattr(avatar_field.widget, "clear_checkbox_label"):
            avatar_field.widget.clear_checkbox_label = "Удалить аватар"
        if avatar_field and hasattr(avatar_field.widget, "input_text"):
            avatar_field.widget.input_text = "Выбрать файл"
        if avatar_field and hasattr(avatar_field.widget, "initial_text"):
            avatar_field.widget.initial_text = "Текущий аватар"


class UserProfileReadOnlyForm(forms.ModelForm):
    """Форма профиля только для чтения (для менеджеров)"""

    class Meta:
        model = CustomUser
        fields = ["phone", "avatar", "username", "first_name", "last_name"]
        labels = {
            "phone": "Телефон",
            "avatar": "Аватар",
            "username": "Логин",
            "first_name": "Имя",
            "last_name": "Фамилия",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Делаем все поля только для чтения
        for field in self.fields:
            self.fields[field].widget.attrs["readonly"] = True
            self.fields[field].widget.attrs["disabled"] = True
            # Убираем обязательность
            self.fields[field].required = False


class UserPasswordResetForm(PasswordResetForm):
    """Форма для ввода email при восстановлении пароля"""

    class Meta:
        model = CustomUser
        fields = ["email"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Настройка поля email
        self.fields["email"].label = "Ваш Email"
        self.fields["email"].widget.attrs.update(
            {"class": "form-control", "placeholder": "ваш@email.com", "autofocus": True}
        )
        self.fields["email"].help_text = "Введите email, указанный при регистрации"


class UserSetPasswordForm(SetPasswordForm):
    """Форма для установки нового пароля (после перехода по ссылке)"""

    def __init__(self, user, *args, **kwargs):
        super().__init__(user, *args, **kwargs)

        # Настройка полей пароля
        self.fields["new_password1"].label = "Новый пароль"
        self.fields["new_password1"].widget.attrs.update(
            {"class": "form-control", "placeholder": "Введите новый пароль"}
        )
        self.fields["new_password1"].help_text = None  # Убираем подсказку

        self.fields["new_password2"].label = "Подтверждение пароля"
        self.fields["new_password2"].widget.attrs.update(
            {"class": "form-control", "placeholder": "Повторите пароль"}
        )
        self.fields["new_password2"].help_text = None
