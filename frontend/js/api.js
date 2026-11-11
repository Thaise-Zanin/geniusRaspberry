const CONFIG = {
  USAR_MOCK: false,
  BASE_URL: 'http://localhost:8000',
  WS_URL: 'ws://localhost:8000/ws',
  TEMPO_COR_MS: 600,
  INTERVALO_MS: 250,
};

const espera = ms => new Promise(r => setTimeout(r, ms));

const ApiReal = {
  async http(caminho, opcoes = {}) {
    const r = await fetch(CONFIG.BASE_URL + caminho, {
      headers: { 'Content-Type': 'application/json' },
      ...opcoes
    });

    if (!r.ok) {
      throw new Error('o servidor respondeu com erro ' + r.status);
    }

    return r.json();
  },

  estatisticas(nome) {
    return this.http('/estatisticas?jogador=' + encodeURIComponent(nome));
  },

  iniciar(nome) {
    return this.http('/partidas', {
      method: 'POST',
      body: JSON.stringify({ jogador: nome })
    });
  },

  conectar(onEvento, onStatus) {
    let ws, fechado = false;
    let resolverPronto;

    const pronto = new Promise(resolve => {
      resolverPronto = resolve;
    });

    const abrir = () => {
      ws = new WebSocket(CONFIG.WS_URL);

      ws.onopen = () => {
        onStatus('conectado');
        resolverPronto();
      };

      ws.onmessage = e => {
        try {
          onEvento(JSON.parse(e.data));
        } catch (_) {}
      };

      ws.onerror = () => onStatus('erro');

      ws.onclose = () => {
        if (!fechado) {
          onStatus('fechado');
          setTimeout(abrir, 2000);
        }
      };
    };

    abrir();

    const desconectar = () => {
      fechado = true;
      ws?.close();
    };

    desconectar.pronto = pronto;

    return desconectar;
  },
};

const ApiMock = (() => {
  const CORES = ['verde', 'vermelho', 'amarelo', 'azul'];
  const CHAVE = 'genius_mock_resultados';

  const SEED = [
    { jogador: 'Ana', nivel: 12, pontuacao: 780, data: '2026-10-28' },
    { jogador: 'Bruno', nivel: 10, pontuacao: 550, data: '2026-10-30' },
    { jogador: 'Carla', nivel: 8, pontuacao: 360, data: '2026-11-02' },
    { jogador: 'Diego', nivel: 6, pontuacao: 210, data: '2026-11-03' },
  ];

  const salvos = () => JSON.parse(localStorage.getItem(CHAVE) || '[]');
  const todos = () => SEED.concat(salvos());
  const maximo = (l, k) => Math.max(0, ...l.map(r => r[k]));
  const sortear = () => CORES[Math.floor(Math.random() * 4)];

  let ouvintes = [], p = null;

  const emitir = e => ouvintes.forEach(f => f(e));

  function enviarSequencia() {
    if (!p) return;

    p.pos = 0;
    p.aceita = false;

    emitir({
      tipo: 'sequencia',
      nivel: p.nivel,
      pontuacao: p.pontos,
      sequencia: [...p.seq]
    });

    setTimeout(() => {
      if (p) p.aceita = true;
    }, p.seq.length * (CONFIG.TEMPO_COR_MS + CONFIG.INTERVALO_MS) + 1800);
  }

  function encerrar() {
    const novoRecorde = p.pontos > maximo(todos(), 'pontuacao');

    localStorage.setItem(CHAVE, JSON.stringify(
      salvos().concat({
        jogador: p.nome,
        nivel: p.nivel,
        pontuacao: p.pontos,
        data: new Date().toISOString().slice(0, 10)
      })
    ));

    emitir({
      tipo: 'fim',
      nivel: p.nivel,
      pontuacao: p.pontos,
      novoRecorde
    });

    p = null;
  }

  return {
    async iniciar(nome) {
      await espera(500);
      p = {
        nome,
        nivel: 1,
        pontos: 0,
        seq: [sortear()]
      };
      setTimeout(enviarSequencia, 300);
      return { partidaId: 'simulada' };
    },

    simularBotao(cor) {
      if (!p || !p.aceita) return;

      if (cor !== p.seq[p.pos]) {
        p.aceita = false;
        emitir({ tipo: 'botao', cor, correto: false });
        setTimeout(encerrar, 500);
        return;
      }

      emitir({ tipo: 'botao', cor, correto: true });

      if (++p.pos === p.seq.length) {
        p.aceita = false;
        p.pontos += p.nivel * 10;

        emitir({
          tipo: 'acerto',
          nivel: p.nivel,
          pontuacao: p.pontos
        });

        p.nivel++;
        p.seq.push(sortear());

        setTimeout(enviarSequencia, 1500);
      }
    },

    async estatisticas(nome) {
      await espera(300);

      const meus = todos().filter(
        r => r.jogador.toLowerCase() === nome.toLowerCase()
      );

      return {
        maiorNivel: maximo(meus, 'nivel'),
        melhorPontuacao: maximo(meus, 'pontuacao'),
        recordeGeral: maximo(todos(), 'pontuacao'),
        partidas: meus.length
      };
    },

    conectar(onEvento) {
      ouvintes.push(onEvento);
      return () => {
        ouvintes = ouvintes.filter(f => f !== onEvento);
      };
    },
  };
})();

const GeniusAPI = CONFIG.USAR_MOCK ? ApiMock : ApiReal;
GeniusAPI.simulado = CONFIG.USAR_MOCK;
