# Convite de Formatura — Alexandra Klippel

Site de convite para a formatura de Alexandra Klippel (Bacharel em Enfermagem, 12/09/2026). Página única em Django com confirmação de presença (RSVP), mural de recados público e contribuição via Pix, no tema visual de uma lamparina de Nightingale e monitor de batimentos (ECG).

## Stack

- Django 6.0
- SQLite
- Alpine.js (formulários e interações)
- Tailwind CSS via CDN (sem build step)
- GSAP + ScrollTrigger/SplitText/DrawSVGPlugin/MotionPathPlugin, Lenis e canvas-confetti (vendorizados como `.min.js`)
- ReportLab (exportação do painel de RSVP em PDF)

## Rodando localmente

```bash
pip install -r requirements.txt
cp .env.example .env    # depois preencha os valores reais
python manage.py migrate
python manage.py runserver
```

Acesse `http://127.0.0.1:8000/`.

## Variáveis de ambiente (`.env`)

| Variável | Descrição |
|---|---|
| `SECRET_KEY` | Obrigatória — o projeto não sobe sem ela. Gere uma nova para cada ambiente. |
| `DEBUG` | `True` só em desenvolvimento. Em produção deve ser `False`. |
| `ALLOWED_HOSTS` | Domínios liberados, separados por vírgula (ex.: `meusite.pythonanywhere.com`). |
| `EMAIL_BACKEND` | `console.EmailBackend` (padrão, só imprime no terminal) ou `smtp.EmailBackend` para enviar de verdade. |
| `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_USE_TLS`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD` | Credenciais SMTP (use uma senha de app do Gmail, não a senha da conta). |
| `EMAIL_DESTINATARIO_CONFIRMACAO` | E-mail que recebe a notificação a cada RSVP. |

Gerar uma nova `SECRET_KEY`:

```bash
python manage.py shell -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

## Comandos úteis

```bash
python manage.py migrate                # aplicar migrações
python manage.py makemigrations convite  # após alterar convite/models.py
python manage.py createsuperuser         # criar acesso ao /painel/
python manage.py shell                   # inspecionar dados (ex.: Recado.objects.count())
python manage.py test convite            # rodar testes
```

## Estrutura

Um único app Django (`convite`), com uma página (`templates/convite/index.html`) organizada em seções: capa, mensagem, contagem regressiva, evento (data/local), festa, mural de recados, RSVP e rodapé.

- `models.py` — `Confirmacao` (RSVP) e `Recado` (mural, público e sem moderação automática — moderação manual pelo `/admin/`).
- `views.py` — endpoints de RSVP e recados (JSON), painel de acompanhamento (`/painel/`, protegido por login) e exportação em PDF.
- `static/convite/css/style.css` — apenas o que não tem equivalente direto em utilitário Tailwind.
- `static/convite/js/main.js` — animações (scroll suave, ritual de abertura, contagem regressiva, divisores em ECG).
