from django.db import models


class Confirmacao(models.Model):
    nome_convidado = models.CharField('nome', max_length=150)
    telefone = models.CharField('telefone', max_length=20, blank=True)
    vai_comparecer = models.BooleanField('vai comparecer')
    mensagem = models.TextField('mensagem', blank=True)
    criado_em = models.DateTimeField('criado em', auto_now_add=True)

    class Meta:
        verbose_name = 'confirmação de presença'
        verbose_name_plural = 'confirmações de presença'
        ordering = ['-criado_em']

    def __str__(self):
        situacao = 'Vai' if self.vai_comparecer else 'Não vai'
        return f'{self.nome_convidado} — {situacao}'


class Recado(models.Model):
    nome_autor = models.CharField('nome', max_length=100)
    mensagem = models.TextField('recado', max_length=300)
    criado_em = models.DateTimeField('criado em', auto_now_add=True)

    class Meta:
        verbose_name = 'recado'
        verbose_name_plural = 'recados'
        ordering = ['-criado_em']

    def __str__(self):
        return f'{self.nome_autor}: {self.mensagem[:40]}'
