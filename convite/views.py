import json
from io import BytesIO
from xml.sax.saxutils import escape

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.utils import timezone
from django.views.decorators.http import require_http_methods
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Table, TableStyle

from .forms import ConfirmacaoForm, RecadoForm
from .models import Confirmacao, Recado

ESMERALDA_ESCURO = colors.HexColor('#0d3a2b')
ESMERALDA = colors.HexColor('#145a41')
CHAMA = colors.HexColor('#e8a54b')
ERRO = colors.HexColor('#c96a6a')
TEXTO_SUAVE = colors.HexColor('#6b6558')
LINHA = colors.HexColor('#ddd4bd')
ZEBRA = colors.HexColor('#f6f2e4')


def index(request):
    recados = list(Recado.objects.values('nome_autor', 'mensagem')[:100])
    return render(request, 'convite/index.html', {'recados_iniciais': recados})


@login_required
def painel(request):
    confirmados = Confirmacao.objects.filter(vai_comparecer=True).order_by('-criado_em')
    recusados = Confirmacao.objects.filter(vai_comparecer=False).order_by('-criado_em')

    contexto = {
        'confirmados': confirmados,
        'recusados': recusados,
        'total_confirmados': confirmados.count(),
        'total_recusados': recusados.count(),
        'total_recados': Recado.objects.count(),
        'nome_formanda': settings.NOME_FORMANDA,
    }
    return render(request, 'convite/painel.html', contexto)


@login_required
def exportar_pdf(request):
    confirmados = Confirmacao.objects.filter(vai_comparecer=True).order_by('-criado_em')
    recusados = Confirmacao.objects.filter(vai_comparecer=False).order_by('-criado_em')

    buffer = BytesIO()
    documento = SimpleDocTemplate(
        buffer, pagesize=A4,
        topMargin=2 * cm, bottomMargin=2 * cm, leftMargin=1.8 * cm, rightMargin=1.8 * cm,
    )
    estilos = getSampleStyleSheet()

    estilo_titulo = ParagraphStyle(
        'TituloFormatura', parent=estilos['Title'],
        textColor=ESMERALDA_ESCURO, fontName='Helvetica-Bold', fontSize=20, spaceAfter=4,
    )
    estilo_subtitulo = ParagraphStyle(
        'Subtitulo', parent=estilos['Normal'],
        textColor=TEXTO_SUAVE, fontName='Helvetica', fontSize=9, spaceAfter=20,
    )
    estilo_secao = ParagraphStyle(
        'Secao', parent=estilos['Heading2'],
        textColor=ESMERALDA, fontName='Helvetica-Bold', fontSize=13, spaceBefore=18, spaceAfter=8,
    )
    estilo_celula = ParagraphStyle('Celula', parent=estilos['Normal'], fontSize=8.5, leading=11)

    def montar_tabela(fila, cor_cabecalho):
        linhas = [['Nome', 'Telefone', 'Mensagem', 'Respondido em']]
        for confirmacao in fila:
            mensagem = escape(confirmacao.mensagem) if confirmacao.mensagem else '—'
            linhas.append([
                Paragraph(escape(confirmacao.nome_convidado), estilo_celula),
                confirmacao.telefone or '—',
                Paragraph(mensagem, estilo_celula),
                timezone.localtime(confirmacao.criado_em).strftime('%d/%m/%Y %H:%M'),
            ])
        tabela = Table(linhas, colWidths=[4 * cm, 3 * cm, 6.7 * cm, 3.3 * cm], repeatRows=1)
        tabela.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), cor_cabecalho),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 8.5),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, ZEBRA]),
            ('GRID', (0, 0), (-1, -1), 0.5, LINHA),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 7),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 7),
        ]))
        return tabela

    elementos = [
        Paragraph(f'Formatura de {settings.NOME_FORMANDA}', estilo_titulo),
        Paragraph(
            f'Lista de confirmações de presença — gerado em '
            f'{timezone.localtime().strftime("%d/%m/%Y às %H:%M")}',
            estilo_subtitulo,
        ),
        Paragraph(f'Confirmados ({confirmados.count()})', estilo_secao),
    ]
    if confirmados:
        elementos.append(montar_tabela(confirmados, ESMERALDA))
    else:
        elementos.append(Paragraph('Ninguém confirmou presença ainda.', estilos['Normal']))

    elementos.append(Paragraph(f'Não vão comparecer ({recusados.count()})', estilo_secao))
    if recusados:
        elementos.append(montar_tabela(recusados, ERRO))
    else:
        elementos.append(Paragraph('Ninguém avisou que não vai, até agora.', estilos['Normal']))

    documento.build(elementos)
    buffer.seek(0)

    nome_arquivo = f'confirmacoes-formatura-{timezone.localtime().strftime("%Y%m%d-%H%M")}.pdf'
    resposta = HttpResponse(buffer.getvalue(), content_type='application/pdf')
    resposta['Content-Disposition'] = f'attachment; filename="{nome_arquivo}"'
    return resposta


@require_http_methods(['POST'])
def confirmar_presenca(request):
    try:
        dados = json.loads(request.body)
    except (json.JSONDecodeError, TypeError):
        dados = request.POST

    form = ConfirmacaoForm(dados)

    if not form.is_valid():
        return JsonResponse({'ok': False, 'erros': form.errors}, status=400)

    confirmacao = form.save()
    _notificar_por_email(confirmacao)

    return JsonResponse({'ok': True})


@require_http_methods(['POST'])
def criar_recado(request):
    try:
        dados = json.loads(request.body)
    except (json.JSONDecodeError, TypeError):
        dados = request.POST

    form = RecadoForm(dados)

    if not form.is_valid():
        return JsonResponse({'ok': False, 'erros': form.errors}, status=400)

    recado = form.save()

    return JsonResponse({
        'ok': True,
        'recado': {
            'nome_autor': recado.nome_autor,
            'mensagem': recado.mensagem,
        },
    })


def falha_csrf(request, reason=''):
    return render(request, '403.html', {'razao_csrf': reason}, status=403)


def _notificar_por_email(confirmacao):
    destinatario = settings.EMAIL_DESTINATARIO_CONFIRMACAO
    if not destinatario:
        return

    situacao = 'VAI comparecer' if confirmacao.vai_comparecer else 'NÃO vai comparecer'
    assunto = f'[Formatura] {confirmacao.nome_convidado} — {situacao}'
    corpo = (
        f'Nome: {confirmacao.nome_convidado}\n'
        f'Telefone: {confirmacao.telefone or "não informado"}\n'
        f'Situação: {situacao}\n'
        f'Mensagem: {confirmacao.mensagem or "-"}\n'
    )

    send_mail(
        assunto,
        corpo,
        settings.DEFAULT_FROM_EMAIL,
        [destinatario],
        fail_silently=True,
    )
