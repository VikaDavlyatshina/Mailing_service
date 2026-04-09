from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import CreateView, UpdateView, DeleteView, ListView, DetailView, TemplateView

from mailing.forms import RecipientForm, MessageForm, MailingForm
from mailing.models import Recipient, Mailing, Message


# Create your views here.

# ==================== ПОЛУЧАТЕЛИ ====================

class RecipientCreateView(CreateView):
    """ Создание получателя рассылки """
    model = Recipient
    form_class = RecipientForm
    template_name = 'includes/form.html'
    success_url = reverse_lazy('mailing:recipient_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Создание получателя'
        context['cancel_url'] = reverse_lazy('mailing:recipient_list')
        return context

class RecipientUpdateView(UpdateView):
    """ Редактирование получателя рассылки """
    model = Recipient
    form_class = RecipientForm
    template_name = 'includes/form.html'
    success_url = reverse_lazy('mailing:recipient_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'✏️ Редактирование: {self.object.email}'
        context['cancel_url'] = reverse_lazy('mailing:recipient_detail', kwargs={'pk': self.object.pk})
        context['button_text'] = 'Сохранить изменения'
        return context

class RecipientListView(ListView):
    """ Просмотр списка получателей """
    model = Recipient
    template_name = 'mailing/recipient_list.html'
    context_object_name = 'recipients'

class RecipientDetailView(DetailView):
    """ Детальный просмотр получателя """
    model = Recipient
    template_name = 'mailing/recipient_detail.html'
    context_object_name = 'recipient'

class RecipientDeleteView(DeleteView):
    """ Удаление получателя рассылки """
    model = Recipient
    template_name = 'includes/confirm_delete.html'
    success_url = reverse_lazy('mailing:recipient_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cancel_url'] = reverse_lazy('mailing:recipient_detail', kwargs={'pk': self.object.pk})
        return context


# ==================== СООБЩЕНИЯ ====================

class MessageCreateView(CreateView):
    """ Создание сообщения """
    model = Message
    form_class = MessageForm
    template_name = 'includes/form.html'
    success_url = reverse_lazy('mailing:message_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = '📝 Создание сообщения'
        context['cancel_url'] = reverse_lazy('mailing:message_list')
        context['button_text'] = 'Создать сообщение'
        return context


class MessageUpdateView(UpdateView):
    """ Редактирование сообщения """
    model = Message
    form_class = MessageForm
    template_name = 'includes/form.html'
    success_url = reverse_lazy('mailing:message_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'✏️ Редактирование: {self.object.subject}'
        context['cancel_url'] = reverse_lazy('mailing:message_detail', kwargs={'pk': self.object.pk})
        context['button_text'] = 'Сохранить изменения'
        return context


class MessageDeleteView(DeleteView):
    """ Удаление сообщения """
    model = Message
    template_name = 'includes/confirm_delete.html'
    success_url = reverse_lazy('mailing:message_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cancel_url'] = reverse_lazy('mailing:message_detail', kwargs={'pk': self.object.pk})
        return context


class MessageListView(ListView):
    """ Список сообщений """
    model = Message
    template_name = 'mailing/message_list.html'
    context_object_name = 'messages'

class MessageDetailView(DetailView):
    """ Детальный просмотр сообщения """
    model = Message
    template_name = 'mailing/message_detail.html'
    context_object_name = 'message'

# ==================== РАССЫЛКИ ====================

class MailingCreateView(CreateView):
    """ Создание рассылки """
    model = Mailing
    form_class = MailingForm
    template_name = 'includes/form.html'
    success_url = reverse_lazy('mailing:mailing_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = '📨 Создание рассылки'
        context['cancel_url'] = reverse_lazy('mailing:mailing_list')
        context['button_text'] = 'Создать рассылку'
        return context


class MailingUpdateView(UpdateView):
    """ Редактирование рассылки """
    model = Mailing
    form_class = MailingForm
    template_name = 'includes/form.html'
    success_url = reverse_lazy('mailing:mailing_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context[
            'title'] = f'✏️ Редактирование рассылки #{self.object.id} - {self.object.message.subject}'
        context['cancel_url'] = reverse_lazy('mailing:mailing_detail', kwargs={'pk': self.object.pk})
        context['button_text'] = 'Сохранить изменения'
        return context


class MailingDeleteView(DeleteView):
    """ Удаление рассылки """
    model = Mailing
    template_name = 'includes/confirm_delete.html'
    success_url = reverse_lazy('mailing:mailing_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cancel_url'] = reverse_lazy('mailing:mailing_detail', kwargs={'pk': self.object.pk})
        return context


class MailingListView(ListView):
    """ Список рассылки """
    model = Mailing
    template_name = 'mailing/mailing_list.html'
    context_object_name = 'mailings'

class MailingDetailView(DetailView):
    """ Детальная информация о рассылке """
    model = Mailing
    template_name = 'mailing/mailing_detail.html'
    context_object_name = 'mailing'

