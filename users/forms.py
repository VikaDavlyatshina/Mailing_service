from django import forms
from django.contrib.auth.forms import UserCreationForm,AuthenticationForm

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
    """ Форма для входа в систему """

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
        fields = ["phone", "avatar", "username", "first_name", "last_name", "birth_date"]

        labels = {
            "first_name": "Имя",
            "last_name": "Фамилия",
            "birth_date": "Дата рождения",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Настраиваем поле avatar
        self._setup_avatar_field()

        # Добавляем placeholder-ы
        self.fields["phone"].widget.attrs["placeholder"] = "+7 (999) 123-45-67"
        self.fields["username"].widget.attrs["placeholder"] = "Укажите логин (опционально)"
        self.fields["first_name"].widget.attrs["placeholder"] = "Ваше имя"
        self.fields["last_name"].widget.attrs["placeholder"] = "Ваша фамилия"

        # 3. Делаем поля необязательными
        self.fields["phone"].required = False
        self.fields["username"].required = False
        self.fields["avatar"].required = False
        self.fields["first_name"].required = False
        self.fields["last_name"].required = False
        self.fields["birth_date"].required = False

    def _setup_avatar_field(self):
        """Настраиваем поле для загрузки аватара."""
        avatar_field = self.fields.get('avatar')
        if avatar_field and isinstance(avatar_field.widget, forms.ClearableFileInput):
            avatar_field.widget.clear_checkbox_label = "Удалить аватар"
            avatar_field.widget.input_text = "Изменить аватар"
            avatar_field.widget.initial_text = "Текущий аватар"
            avatar_field.widget.attrs['accept'] = 'image/*'

