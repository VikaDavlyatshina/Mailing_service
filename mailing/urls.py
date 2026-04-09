from django.urls import path
from mailing.apps import MailingConfig
from mailing import views

app_name = MailingConfig.name

urlpatterns = [
    # ==================== ГЛАВНАЯ ====================
    path('', views.HomeView.as_view(), name='home'),

    # ==================== ПОЛУЧАТЕЛИ ====================
    # Список
    path('recipients/', views.RecipientListView.as_view(), name='recipient_list'),
    # Создание
    path('recipients/create/', views.RecipientCreateView.as_view(), name='recipient_create'),
    # Детально
    path('recipients/<int:pk>/', views.RecipientDetailView.as_view(), name='recipient_detail'),
    # Редактирование
    path('recipients/<int:pk>/update/', views.RecipientUpdateView.as_view(), name='recipient_update'),
    # Удаление
    path('recipients/<int:pk>/delete/', views.RecipientDeleteView.as_view(), name='recipient_delete'),

    # ==================== СООБЩЕНИЯ ====================
    # Список
    path('messages/', views.MessageListView.as_view(), name='message_list'),
    # Создание
    path('messages/create/', views.MessageCreateView.as_view(), name='message_create'),
    # Детально
    path('messages/<int:pk>/', views.MessageDetailView.as_view(), name='message_detail'),
    # Редактирование
    path('messages/<int:pk>/update/', views.MessageUpdateView.as_view(), name='message_update'),
    # Удаление
    path('messages/<int:pk>/delete/', views.MessageDeleteView.as_view(), name='message_delete'),

    # ==================== РАССЫЛКИ ====================
    # Список
    path('mailings/', views.MailingListView.as_view(), name='mailing_list'),
    # Создание
    path('mailings/create/', views.MailingCreateView.as_view(), name='mailing_create'),
    # Детально
    path('mailings/<int:pk>/', views.MailingDetailView.as_view(), name='mailing_detail'),
    # Редактирование
    path('mailings/<int:pk>/update/', views.MailingUpdateView.as_view(), name='mailing_update'),
    # Удаление
    path('mailings/<int:pk>/delete/', views.MailingDeleteView.as_view(), name='mailing_delete'),
]