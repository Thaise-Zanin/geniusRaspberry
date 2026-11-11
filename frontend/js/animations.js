const Animacoes = (() => {
  let ocupado = false;

  async function acender(pad, ms) {
    pad.classList.add('ativo');
    await espera(ms);
    pad.classList.remove('ativo');
  }

  async function tocarSequencia(
    sequencia,
    pads,
    { duracao = 600, intervalo = 250 } = {}
  ) {
    if (ocupado) return false;

    ocupado = true;

    try {
      for (const cor of sequencia) {
        if (pads[cor]) {
          await acender(pads[cor], duracao);
          await espera(intervalo);
        }
      }
    } finally {
      ocupado = false;
    }

    return true;
  }

  async function piscar(pad, ms = 100) {
    if (ocupado || !pad) return false;

    ocupado = true;

    try {
      await acender(pad, ms);
    } finally {
      ocupado = false;
    }

    return true;
  }

  return {
    tocarSequencia,
    piscar
  };
})();
