from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

app_name = 'convite'

urlpatterns = [
    path('', views.index, name='index'),
    path('confirmar/', views.confirmar_presenca, name='confirmar_presenca'),
    path('recados/', views.criar_recado, name='criar_recado'),
    path('painel/', views.painel, name='painel'),
    path('painel/exportar/', views.exportar_pdf, name='exportar_pdf'),
    path(
        'painel/entrar/',
        auth_views.LoginView.as_view(template_name='convite/painel_login.html'),
        name='login',
    ),
    path(
        'painel/sair/',
        auth_views.LogoutView.as_view(),
        name='logout',
    ),
]
