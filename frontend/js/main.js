/* main.js — utilidades comuns, cabeçalho e lógica do dashboard. */
const $ = s => document.querySelector(s);
const esc = s => String(s).replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
const pad2 = n => String(n).padStart(2, '0');
const nomeSalvo = () => localStorage.getItem('genius_nome') || '';
const salvarNome = n => localStorage.setItem('genius_nome', n);
const formatarData = d => { const x = new Date(d); return isNaN(x) ? '—' : x.toLocaleDateString('pt-BR', { timeZone: 'UTC' }); };

function renderCabecalho() {
  const { raiz = '', pagina } = document.body.dataset;
  const link = (id, href, t) => `<a href="${raiz}${href}" ${pagina === id ? 'aria-current="page"' : ''}>${t}</a>`;
  $('#topo').innerHTML = `<a class="logo" href="${raiz}index.html" aria-label="Genius, início">GENIUS
    <span><i style="background:var(--verde)"></i><i style="background:var(--vermelho)"></i><i style="background:var(--amarelo)"></i><i style="background:var(--azul)"></i></span></a>
    <nav>${link('inicio', 'index.html', 'Início')}${link('jogo', 'pages/jogo.html', 'Jogar')}`; //${link('ranking', 'pages/ranking.html', 'Ranking')}</nav>
}

async function iniciarDashboard() {
  const campo = $('#nome');
  campo.value = nomeSalvo();
  $('#btn-iniciar').addEventListener('click', () => salvarNome(campo.value.trim() || 'Jogador'));

  // demonstração: o painel do topo pisca uma sequência aleatória em loop
  const pads = {};
  document.querySelectorAll('#demo .pad').forEach(p => pads[p.dataset.cor] = p);
  if (!matchMedia('(prefers-reduced-motion: reduce)').matches) {
    const cores = Object.keys(pads);
    (async () => { for (;;) { await espera(2200); await Animacoes.tocarSequencia(Array.from({ length: 4 }, () => cores[Math.floor(Math.random() * 4)]), pads, { duracao: 420, intervalo: 180 }); } })();
  }

  const aviso = $('#aviso');
  try {
    const nome = nomeSalvo() || 'Jogador';
    const [s, rank] = await Promise.all([GeniusAPI.estatisticas(nome), GeniusAPI.ranking()]);
    $('#s-nivel').textContent = s.maiorNivel; $('#s-melhor').textContent = s.melhorPontuacao;
    $('#s-recorde').textContent = s.recordeGeral; $('#s-partidas').textContent = s.partidas;
    const top = rank.slice().sort((a, b) => b.pontuacao - a.pontuacao).slice(0, 3);
    $('#top3').innerHTML = top.length ? top.map((r, i) => `<div class="linha"><span class="pos p${i + 1}">${i + 1}</span><strong>${esc(r.jogador)}</strong><small>Nível ${r.nivel}</small><span>${r.pontuacao} pts</span></div>`).join('')
      : '<p>Ainda não há resultados. Seja o primeiro a jogar!</p>';
  } catch (e) {
    aviso.hidden = false; aviso.textContent = 'Não foi possível carregar os dados do servidor: ' + e.message + '.';
    $('#top3').textContent = '';
  }
}

renderCabecalho();
if (document.body.dataset.pagina === 'inicio') iniciarDashboard();
