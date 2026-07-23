(function () {
  gsap.registerPlugin(ScrollTrigger, SplitText, DrawSVGPlugin, MotionPathPlugin);

  const prefereReduzido = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  let lenis = null;

  function iniciarSmoothScroll() {
    if (prefereReduzido || typeof Lenis === 'undefined') return;
    lenis = new Lenis({ duration: 1.15, smoothWheel: true });
    lenis.on('scroll', ScrollTrigger.update);
    gsap.ticker.add((tempo) => lenis.raf(tempo * 1000));
    gsap.ticker.lagSmoothing(0);
  }

  function iniciarAncoras() {
    document.querySelectorAll('a[href^="#"]').forEach((link) => {
      link.addEventListener('click', (evento) => {
        const alvo = document.getElementById(link.getAttribute('href').slice(1));
        if (!alvo) return;
        evento.preventDefault();
        if (lenis) {
          lenis.scrollTo(alvo, { duration: 1.3 });
        } else {
          alvo.scrollIntoView({ behavior: prefereReduzido ? 'auto' : 'smooth' });
        }
      });
    });
  }

  function criarParticulas(canvas, opcoes = {}) {
    if (!canvas || prefereReduzido) return () => {};

    const ctx = canvas.getContext('2d');
    let w = 0;
    let h = 0;
    let particulas = [];
    let rafId = null;
    let rodando = true;

    function redimensionar() {
      w = canvas.width = canvas.offsetWidth;
      h = canvas.height = canvas.offsetHeight;
    }

    function criar(n) {
      particulas = Array.from({ length: n }, () => ({
        x: Math.random() * w,
        y: Math.random() * h,
        r: Math.random() * 1.8 + 0.4,
        vy: Math.random() * 0.35 + 0.08,
        vx: (Math.random() - 0.5) * 0.15,
        alpha: Math.random() * 0.5 + 0.15,
      }));
    }

    function passo() {
      if (!rodando) return;
      if (!document.hidden) {
        ctx.clearRect(0, 0, w, h);
        particulas.forEach((p) => {
          p.y -= p.vy;
          p.x += p.vx;
          if (p.y < -10) {
            p.y = h + 10;
            p.x = Math.random() * w;
          }
          ctx.beginPath();
          ctx.fillStyle = `rgba(240, 194, 116, ${p.alpha})`;
          ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
          ctx.fill();
        });
      }
      rafId = requestAnimationFrame(passo);
    }

    redimensionar();
    criar(opcoes.quantidade || 40);
    window.addEventListener('resize', redimensionar);
    passo();

    return () => {
      rodando = false;
      if (rafId) cancelAnimationFrame(rafId);
      window.removeEventListener('resize', redimensionar);
    };
  }

  function iniciarRitual() {
    const ritual = document.getElementById('ritual');
    if (!ritual) return;

    if (sessionStorage.getItem('formatura_ritual_aberto')) {
      ritual.remove();
      revelarHero(true);
      return;
    }

    document.body.style.overflow = 'hidden';

    const chama = ritual.querySelector('.lamparina__chama');
    const tracos = ritual.querySelectorAll(
      '.lamparina__pavio, .lamparina__alca, .lamparina__corpo, .lamparina__base, .lamparina__pe'
    );
    const glow = document.getElementById('ritual-glow');
    const botaoAcender = document.getElementById('botao-acender');
    const botaoPular = document.getElementById('botao-pular');

    gsap.set(chama, { transformOrigin: '50% 70%', scale: 0.4, opacity: 0 });

    let pararBrasas = () => {};

    if (!prefereReduzido) {
      gsap.set(tracos, { drawSVG: '0%' });
      gsap.to(tracos, { drawSVG: '100%', duration: 2.2, ease: 'power2.inOut', stagger: 0.15 });
      pararBrasas = criarParticulas(document.getElementById('tela-brasas'), { quantidade: 24 });
    } else {
      gsap.set(tracos, { drawSVG: '100%' });
    }

    function abrir(instantaneo) {
      sessionStorage.setItem('formatura_ritual_aberto', '1');

      const finalizar = () => {
        document.body.style.overflow = '';
        pararBrasas();
        ritual.remove();
        revelarHero(false);
      };

      if (instantaneo || prefereReduzido) {
        gsap.to(ritual, { opacity: 0, duration: 0.4, onComplete: finalizar });
        return;
      }

      ritual.classList.add('ritual--acesa');
      const tl = gsap.timeline({ onComplete: finalizar });
      tl.to(chama, { scale: 1, opacity: 1, duration: 0.5, ease: 'back.out(2)' })
        .to(glow, { scale: 60, opacity: 1, duration: 1.1, ease: 'power2.in' }, '-=0.15')
        .to(ritual, { opacity: 0, duration: 0.6 }, '-=0.35')
        .to(glow, { opacity: 0, duration: 0.3 }, '-=0.3');
    }

    botaoAcender.addEventListener('click', () => abrir(false));
    botaoPular.addEventListener('click', () => abrir(true));
  }

  function revelarHero(instantaneo) {
    const nome = document.querySelector('[data-split-nome]');
    const moldura = document.querySelector('.capa__foto-moldura');
    const linhas = document.querySelectorAll('.hero-linha');

    if (instantaneo || prefereReduzido || !nome || typeof SplitText === 'undefined') {
      gsap.set(moldura, { opacity: 1, scale: 1 });
      gsap.set(linhas, { opacity: 1, y: 0 });
      criarParticulas(document.getElementById('tela-particulas'), { quantidade: 30 });
      return;
    }

    const split = new SplitText(nome, { type: 'words, chars' });
    gsap.set(split.chars, { opacity: 0, y: 34, filter: 'blur(6px)' });
    gsap.set(moldura, { opacity: 0, scale: 0.82 });
    gsap.set(linhas, { opacity: 0, y: 18 });

    gsap
      .timeline({ defaults: { ease: 'power3.out' } })
      .to(moldura, { opacity: 1, scale: 1, duration: 0.9, ease: 'back.out(1.6)' })
      .to(split.chars, { opacity: 1, y: 0, filter: 'blur(0px)', duration: 0.7, stagger: 0.018 }, '-=0.55')
      .to(linhas, { opacity: 1, y: 0, duration: 0.8, stagger: 0.12 }, '-=0.4');

    criarParticulas(document.getElementById('tela-particulas'), { quantidade: 30 });
  }

  function iniciarRevelacaoAoRolar() {
    gsap.utils.toArray('.reveal').forEach((el) => {
      gsap.to(el, {
        opacity: 1,
        y: 0,
        duration: 1,
        ease: 'power2.out',
        scrollTrigger: { trigger: el, start: 'top 82%' },
      });
    });
  }

  function iniciarDivisores() {
    document.querySelectorAll('[data-divisor]').forEach((divisor) => {
      const traco = divisor.querySelector('.divisor__uso');
      const blip = divisor.querySelector('.divisor__blip');
      if (!traco) return;

      if (prefereReduzido) {
        gsap.set(traco, { drawSVG: '100%' });
        return;
      }

      gsap.set(traco, { drawSVG: '0%' });
      gsap.to(traco, {
        drawSVG: '100%',
        ease: 'none',
        scrollTrigger: { trigger: divisor, start: 'top 90%', end: 'bottom 60%', scrub: 0.6 },
      });

      if (blip) {
        gsap.set(blip, { opacity: 1 });
        gsap.to(blip, {
          motionPath: { path: traco, align: traco, alignOrigin: [0.5, 0.5] },
          duration: 2.6,
          repeat: -1,
          ease: 'power1.inOut',
          scrollTrigger: { trigger: divisor, start: 'top bottom', end: 'bottom top', toggleActions: 'play pause play pause' },
        });
      }
    });
  }

  function iniciarContagemRegressiva() {
    const container = document.querySelector('.contagem');
    if (!container) return;

    const dataAlvo = new Date(container.dataset.dataAlvo).getTime();
    const spanDias = container.querySelector('[data-unidade="dias"]');
    const spanHoras = container.querySelector('[data-unidade="horas"]');
    const spanMinutos = container.querySelector('[data-unidade="minutos"]');
    const spanSegundos = container.querySelector('[data-unidade="segundos"]');

    function atualizar() {
      const restante = dataAlvo - Date.now();

      if (restante <= 0) {
        [spanDias, spanHoras, spanMinutos, spanSegundos].forEach((s) => (s.textContent = '00'));
        clearInterval(intervalo);
        return;
      }

      const dias = Math.floor(restante / 86400000);
      const horas = Math.floor((restante / 3600000) % 24);
      const minutos = Math.floor((restante / 60000) % 60);
      const segundos = Math.floor((restante / 1000) % 60);

      spanDias.textContent = String(dias).padStart(2, '0');
      spanHoras.textContent = String(horas).padStart(2, '0');
      spanMinutos.textContent = String(minutos).padStart(2, '0');
      spanSegundos.textContent = String(segundos).padStart(2, '0');
    }

    atualizar();
    const intervalo = setInterval(atualizar, 1000);
  }

  function iniciarBotoesMagneticos() {
    if (prefereReduzido || !window.matchMedia('(pointer: fine)').matches) return;

    document.querySelectorAll('[data-magnetico]').forEach((botao) => {
      botao.addEventListener('mousemove', (evento) => {
        const rect = botao.getBoundingClientRect();
        const x = evento.clientX - rect.left - rect.width / 2;
        const y = evento.clientY - rect.top - rect.height / 2;
        gsap.to(botao, { x: x * 0.25, y: y * 0.3, duration: 0.4, ease: 'power2.out' });
      });
      botao.addEventListener('mouseleave', () => {
        gsap.to(botao, { x: 0, y: 0, duration: 0.5, ease: 'elastic.out(1, 0.4)' });
      });
    });
  }

  document.addEventListener('DOMContentLoaded', () => {
    iniciarSmoothScroll();
    iniciarAncoras();
    iniciarRitual();
    iniciarRevelacaoAoRolar();
    iniciarDivisores();
    iniciarContagemRegressiva();
    iniciarBotoesMagneticos();

    if (document.fonts && document.fonts.ready) {
      document.fonts.ready.then(() => ScrollTrigger.refresh());
    }
  });
})();
