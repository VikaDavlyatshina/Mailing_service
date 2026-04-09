from django import forms
from .models import Recipient, Message, Mailing

class BootstrapFormMixin:
    """
    Миксин для автоматической стилизации форм Bootstrap.

    Что делает:
    - Добавляет class='form-control' к обычным полям
    - Добавляет class='form-select' к выпадающим спискам
    - Добавляет class='form-check-input' к чекбоксам
    - Автоматически добавляет placeholder из названия поля

    Использование:
        class MyForm(BootstrapFormMixin, forms.ModelForm):
            class Meta:
                model = MyModel
                fields = '__all__'
    """

    def __init__(self, *args, **kwargs):
        """
        Конструктор миксина.

        *args — позиционные аргументы (например, данные из POST-запроса)
        **kwargs — именованные аргументы (например, instance=product)
        """

        # Вызываем конструктор родительского класса
        super().__init__(*args, **kwargs)

        # Перебираем все поля формы
        # self.fields — словарь {'имя_поля': объект_поля}
        for field_name, field in self.fields.items():
            # Получаем виджет поля — он отвечает за HTML-отображение
            widget = field.widget

            # ========== 1. ОПРЕДЕЛЯЕМ CSS КЛАСС ==========
            # Выпадающие списки (<select>) — используем form-select
            if isinstance(widget, (forms.Select, forms.SelectMultiple)):
                css_class = 'form-select'
            # Чекбоксы (<input type="checkbox">) — используем form-check-input
            elif isinstance(widget, forms.CheckboxInput):
                css_class = 'form-check-input'
            else:
                # Все остальные поля — используем form-control
                css_class = 'form-control'

            # ========== 2. ДОБАВЛЯЕМ CSS КЛАСС К ВИДЖЕТУ ==========
            # widget.attrs — словарь HTML-атрибутов (class, placeholder, id и т.д.)

            if 'class' in widget.attrs:
                # Если класс уже есть — добавляем новый через пробел
                widget.attrs['class'] += f' {css_class}'
            else:
                # Если класса нет — просто ставим наш класс
                widget.attrs['class'] = css_class

            # ========== 3. ДОБАВЛЯЕМ PLACEHOLDER ДЛЯ ТЕКСТОВЫХ ПОЛЕЙ ==========
            # Проверяем, что это текстовое поле (не чекбокс, не выпадающий список)
            if isinstance(widget, (forms.TextInput, forms.EmailInput, forms.Textarea)):

                # Добавляем placeholder, только если:
                # 1) placeholder ещё не задан (чтобы не перезаписать явный)
                # 2) у поля есть label (чтобы было что вставить)
                if 'placeholder' not in widget.attrs and field.label:
                    # Создаём placeholder: "Введите Имя поля"
                    widget.attrs['placeholder'] = f'Введите {field.label.lower()}'



class RecipientForm(BootstrapFormMixin, forms.ModelForm):
    """Форма для получателя"""

    class Meta:
        model = Recipient
        fields = ['email', 'full_name', 'comment']
        labels = {
            'email': 'Email адрес',
            'full_name': 'ФИО получателя',
            'comment': 'Комментарий',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Специфичные настройки, которые не вынесены в миксин
        self.fields['comment'].widget.attrs['rows'] = 3
        self.fields['email'].widget.attrs['placeholder'] = 'example@mail.ru'
        self.fields['full_name'].widget.attrs['placeholder'] = 'Иванов Иван Иванович'


class MessageForm(BootstrapFormMixin, forms.ModelForm):
    """Форма для сообщения"""

    class Meta:
        model = Message
        fields = ['subject', 'email_body']
        labels = {
            'subject': 'Тема письма',
            'email_body': 'Тело письма',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['email_body'].widget.attrs['rows'] = 10
        self.fields['subject'].widget.attrs['placeholder'] = 'Тема письма'


class MailingForm(BootstrapFormMixin, forms.ModelForm):
    """Форма для рассылки"""

    class Meta:
        model = Mailing
        fields = ['start_time', 'end_time', 'message', 'recipients']
        labels = {
            'start_time': 'Дата и время начала',
            'end_time': 'Дата и время окончания',
            'message': 'Сообщение',
            'recipients': 'Получатели',
        }
        help_texts = {
            'start_time': 'Формат: ГГГГ-ММ-ДД ЧЧ:ММ',
            'end_time': 'Формат: ГГГГ-ММ-ДД ЧЧ:ММ',
            'recipients': 'Удерживайте Ctrl для выбора нескольких получателей',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Дополнительные настройки
        self.fields['recipients'].widget.attrs['size'] = 8