/* jogo.js — só mostra o que o servidor manda. Não valida jogadas. */
(function () {
  const pads = {};
  document.querySelectorAll('.pad').forEach(p => { pads[p.dataset.cor] = p; p.addEventListener('click', () => { if (GeniusAPI.simulado && estado === 'jogador') GeniusAPI.simularBotao(p.dataset.cor); }); });
  let estado = 'ocioso';            // ocioso | carregando | mostrando | jogador | acerto | fim
  let fila = Promise.resolve();     // eventos do servidor são tratados um por vez, na ordem
  let desconectar = null, rodada = { tamanho: 0, feitos: 0 }, recorde = 0;

  const msg = t => $('#mensagem').textContent = t;
  const status = t => $('#status').textContent = t;
  const aviso = t => { $('#aviso').hidden = !t; $('#aviso').textContent = t || ''; };
  function placar(nivel, pontos) {
    $('#nivel').textContent = pad2(nivel); $('#centro-nivel').textContent = nivel;
    $('#pontos').textContent = pontos; $('#prog-nivel').textContent = 'Nível ' + pad2(nivel);
  }
  function progresso() {
    const { tamanho, feitos } = rodada;
    $('#prog-seq').textContent = `Sequência atual: ${tamanho} ${tamanho === 1 ? 'cor' : 'cores'}`;
    $('#barra').style.width = tamanho ? feitos / tamanho * 100 + '%' : '0%';
  }
  function cliques(on) {
    Object.values(pads).forEach(p => { p.classList.toggle('clicavel', on && GeniusAPI.simulado); p.tabIndex = on && GeniusAPI.simulado ? 0 : -1; });
  }
  const bloquearCampos = b => { $('#nome').disabled = b; $('#btn-iniciar').disabled = b; };

  async function iniciar() {
    if (estado !== 'ocioso' && estado !== 'fim') return;
    const nome = $('#nome').value.trim() || 'Jogador';
    salvarNome(nome); $('#final').hidden = true; aviso('');
    estado = 'carregando'; bloquearCampos(true);
    status('Conectando'); msg('Conectando ao servidor...'); placar(1, 0); rodada = { tamanho: 0, feitos: 0 }; progresso();
    try {
      if (desconectar) desconectar();
      desconectar = GeniusAPI.conectar(ev => { fila = fila.then(() => tratar(ev)).catch(console.error); },
        s => aviso(s === 'conectado' ? '' : 'Conexão com o servidor perdida. Tentando reconectar...'));
      await GeniusAPI.iniciar(nome);
      status('Em andamento'); msg('Prepare-se!');
    } catch (e) {
      estado = 'ocioso'; bloquearCampos(false); status('Parado'); msg('Não foi possível iniciar a partida.');
      aviso('Erro: ' + e.message + '. Verifique se o servidor está ligado e tente de novo.');
    }
  }

  async function tratar(ev) {
    switch (ev.tipo) {
      case 'sequencia':
        estado = 'mostrando'; cliques(false); status('Mostrando');
        placar(ev.nivel, ev.pontuacao); rodada = { tamanho: ev.sequencia.length, feitos: 0 }; progresso();
        msg(ev.nivel > 1 ? 'Nova sequência chegando...' : 'Prepare-se!'); await espera(1000);
        msg('Memorize a sequência...');
        await Animacoes.tocarSequencia(ev.sequencia, pads, { duracao: CONFIG.TEMPO_COR_MS, intervalo: CONFIG.INTERVALO_MS });
        estado = 'jogador'; status('Sua vez'); msg('Sua vez! Reproduza a sequência no hardware.'); cliques(true);
        break;
      case 'botao':
        await Animacoes.piscar(pads[ev.cor]);
        if (ev.correto === false) { const t = $('#tabuleiro'); t.classList.add('shake'); setTimeout(() => t.classList.remove('shake'), 400); }
        else { rodada.feitos++; progresso(); }
        break;
      case 'acerto':
        estado = 'acerto'; cliques(false); status('Acertou'); $('#pontos').textContent = ev.pontuacao;
        msg('Muito bem! Você acertou!'); await espera(1200);
        break;
      case 'fim':
        estado = 'fim'; cliques(false); status('Fim'); msg('Fim de jogo!'); placar(ev.nivel, ev.pontuacao);
        if (ev.pontuacao > recorde) { recorde = ev.pontuacao; $('#recorde').textContent = recorde; }
        $('#f-nivel').textContent = ev.nivel; $('#f-pontos').textContent = ev.pontuacao; $('#f-recorde').hidden = !ev.novoRecorde;
        $('#final').hidden = false; bloquearCampos(false); $('#btn-iniciar').textContent = 'JOGAR DE NOVO';
        if (desconectar) { desconectar(); desconectar = null; }
        break;
    }
  }

  $('#btn-iniciar').addEventListener('click', iniciar);
  $('#btn-de-novo').addEventListener('click', iniciar);
  $('#nome').value = nomeSalvo();
  $('#nota-sim').hidden = !GeniusAPI.simulado;
  GeniusAPI.estatisticas(nomeSalvo() || 'Jogador').then(s => { recorde = s.melhorPontuacao; $('#recorde').textContent = recorde; }).catch(() => aviso('Não foi possível carregar seu recorde.'));
  if (location.hash === '#iniciar') iniciar();
})();
