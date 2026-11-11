const $ = s => document.querySelector(s);

const esc = s => String(s).replace(/[&<>"']/g, c => ({
  '&': '&amp;',
  '<': '&lt;',
  '>': '&gt;',
  '"': '&quot;',
  "'": '&#39;'
}[c]));

const pad2 = n => String(n).padStart(2, '0');

const nomeSalvo = () => localStorage.getItem('genius_nome') || '';

const salvarNome = n => localStorage.setItem('genius_nome', n);

const formatarData = d => {
  const x = new Date(d);
  return isNaN(x) ? '—' : x.toLocaleDateString('pt-BR', {
    timeZone: 'UTC'
  });
};

function renderCabecalho() {
  const { raiz = '', pagina } = document.body.dataset;

  const link = (id, href, t) =>
    `<a href="${raiz}${href}" ${pagina === id ? 'aria-current="page"' : ''}>${t}</a>`;

  $('#topo').innerHTML = `
    <a class="logo" href="${raiz}index.html" aria-label="Genius, início">
      GENIUS
      <span>
        <i style="background:var(--verde)"></i>
        <i style="background:var(--vermelho)"></i>
        <i style="background:var(--amarelo)"></i>
        <i style="background:var(--azul)"></i>
      </span>
    </a>
    <nav>
      ${link('inicio', 'index.html', 'Início')}
      ${link('jogo', 'pages/jogo.html', 'Jogar')}
    </nav>
  `;
}

async function iniciarDashboard() {
  const campo = $('#nome');

  campo.value = nomeSalvo();

  $('#btn-iniciar').addEventListener('click', () => {
    salvarNome(campo.value.trim() || 'Jogador');
  });

  // Demonstração: o painel do topo pisca uma sequência aleatória em loop.
  const pads = {};

  document.querySelectorAll('#demo .pad').forEach(p => {
    pads[p.dataset.cor] = p;
  });

  if (!matchMedia('(prefers-reduced-motion: reduce)').matches) {
    const cores = Object.keys(pads);

    (async () => {
      for (;;) {
        await espera(2200);

        await Animacoes.tocarSequencia(
          Array.from(
            { length: 4 },
            () => cores[Math.floor(Math.random() * cores.length)]
          ),
          pads,
          { duracao: 420, intervalo: 180 }
        );
      }
    })();
  }

  const aviso = $('#aviso');

  try {
    const nome = nomeSalvo() || 'Jogador';
    const s = await GeniusAPI.estatisticas(nome);

    $('#s-nivel').textContent = s.maiorNivel ?? s.maior_nivel ?? 0;
    $('#s-melhor').textContent = s.melhorPontuacao ?? s.melhor_pontuacao ?? 0;
    $('#s-partidas').textContent = s.partidas ?? 0;

  } catch (e) {
    aviso.hidden = false;
    aviso.textContent =
      'Não foi possível carregar as estatísticas do servidor: ' +
      e.message + '.';
  }
}

renderCabecalho();

if (document.body.dataset.pagina === 'inicio') {
  iniciarDashboard();
}
