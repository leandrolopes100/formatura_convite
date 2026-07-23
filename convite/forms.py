import re

from django import forms

from .models import Confirmacao, Recado

NOME_PATTERN = re.compile(r"^[A-Za-zÀ-ÿ'\-\s]+$")


def limpar_nome_completo(nome):
    nome = re.sub(r'\s+', ' ', nome.strip())

    if not NOME_PATTERN.match(nome):
        raise forms.ValidationError('Digite um nome usando só letras.')

    partes = nome.split(' ')
    if len(partes) < 2 or any(len(parte) < 2 for parte in partes):
        raise forms.ValidationError('Digite seu nome completo (nome e sobrenome).')

    return nome


def limpar_telefone(telefone):
    telefone = telefone.strip()
    if not telefone:
        return telefone

    digitos = re.sub(r'\D', '', telefone)
    if len(digitos) not in (10, 11):
        raise forms.ValidationError('Digite um telefone válido, com DDD.')

    return telefone


class ConfirmacaoForm(forms.ModelForm):
    class Meta:
        model = Confirmacao
        fields = [
            'nome_convidado',
            'telefone',
            'vai_comparecer',
            'mensagem',
        ]

    def clean_nome_convidado(self):
        return limpar_nome_completo(self.cleaned_data['nome_convidado'])

    def clean_telefone(self):
        return limpar_telefone(self.cleaned_data['telefone'])


class RecadoForm(forms.ModelForm):
    class Meta:
        model = Recado
        fields = ['nome_autor', 'mensagem']

    def clean_nome_autor(self):
        return limpar_nome_completo(self.cleaned_data['nome_autor'])
