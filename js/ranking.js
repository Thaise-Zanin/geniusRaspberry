/* ranking.js — tabela de melhores resultados. */
(function () {
  const aviso = $('#aviso'), vazio = $('#vazio'), tabela = $('#tabela'), btn = $('#btn-atualizar');
  async function carregar() {
    btn.disabled = true; aviso.hidden = false; aviso.className = 'aviso info'; aviso.textContent = 'Carregando ranking...';
    try {
      const dados = (await GeniusAPI.ranking()).slice().sort((a, b) => b.pontuacao - a.pontuacao);
      aviso.hidden = true; vazio.hidden = dados.length > 0; tabela.hidden = dados.length === 0;
      $('#corpo').innerHTML = dados.map((r, i) => `<tr class="${i < 3 ? 'p' + (i + 1) : ''}"><td><span class="pos ${i < 3 ? 'p' + (i + 1) : ''}">${i + 1}</span></td><td><strong>${esc(r.jogador)}</strong></td><td>${r.nivel}</td><td>${r.pontuacao}</td><td>${formatarData(r.data)}</td></tr>`).join('');
    } catch (e) {
      aviso.className = 'aviso'; aviso.textContent = 'Não foi possível carregar o ranking: ' + e.message + '. Tente atualizar.';
    }
    btn.disabled = false;
  }
  btn.addEventListener('click', carregar);
  carregar();
})();
