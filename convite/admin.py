from django.contrib import admin

from .models import Confirmacao, Recado


@admin.register(Confirmacao)
class ConfirmacaoAdmin(admin.ModelAdmin):
    list_display = (
        'nome_convidado',
        'vai_comparecer',
        'telefone',
        'criado_em',
    )
    list_filter = ('vai_comparecer',)
    search_fields = ('nome_convidado', 'telefone')
    ordering = ('-criado_em',)


@admin.register(Recado)
class RecadoAdmin(admin.ModelAdmin):
    list_display = ('nome_autor', 'mensagem', 'criado_em')
    search_fields = ('nome_autor', 'mensagem')
    ordering = ('-criado_em',)
