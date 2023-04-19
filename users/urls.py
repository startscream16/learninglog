"""Определяет схемы URL для users"""

from django.urls import path, include

from . import views

app_name = 'users'
urlpatterns = [
    # Включает URL-адреса аутентификации по умолчанию
    path('', include('django.contrib.auth.urls')),
    # Страница регистрации
    path('register/', views.register, name='register'),
]
