//Função chamada no rodapé
document.getElementById('anoAtual').textContent = new Date().getFullYear();

// --- Vagas fictícias ---
var vagas = [
  { nome: 'Garagem Central',       endereco: 'Rua das Flores, 142 – Centro',           preco: 'R$ 8/hora',  tipo: 'coberta', avaliacao: '⭐ 4.9' },
  { nome: 'Estacionamento Premium', endereco: 'Av. Brasil, 500 – Centro',              preco: 'R$ 10/hora', tipo: 'coberta', avaliacao: '⭐ 4.8' },
  { nome: 'Vaga Ana Silva',         endereco: 'Rua Pioneiro, 88 – Zona 7',             preco: 'R$ 6/hora',  tipo: 'aberta',  avaliacao: '⭐ 4.7' },
  { nome: 'Garagem do João',        endereco: 'Rua Paraíba, 210 – Jardim Alvorada',    preco: 'R$ 5/hora',  tipo: 'aberta',  avaliacao: '⭐ 4.6' },
  { nome: 'Vaga Segura Express',    endereco: 'Av. Colombo, 1200 – Centro',            preco: 'R$ 9/hora',  tipo: 'coberta', avaliacao: '⭐ 5.0' }
];


// Monta o HTML de um card de vaga
function montarCardVaga(vaga) {
  return `
    <div class="card-vaga">
      <div class="topo-vaga">
        <span class="nome-vaga">${vaga.nome}</span>
        <span class="tipo-vaga ${vaga.tipo}">${vaga.tipo}</span>
      </div>
      <p class="endereco-vaga">📍 ${vaga.endereco}</p>
      <div class="rodape-vaga">
        <span class="preco-vaga">${vaga.preco}</span>
        <span class="avaliacao-vaga">${vaga.avaliacao}</span>
      </div>
      <button class="btn-reservar" onclick="reservar(this)">Reservar</button>
    </div>
  `;
}

// --- Busca de vagas ---
document.getElementById('btnBuscar').addEventListener('click', function () {
  var cidade = document.getElementById('cidade').value;
  var bairro = document.getElementById('bairro').value.trim();
  var data   = document.getElementById('data').value;
  var area   = document.getElementById('resultados');

  if (!cidade || !bairro || !data) {
    area.innerHTML = '<p class="placeholder-resultado">⚠️ Preencha todos os campos antes de buscar.</p>';
    return;
  }

  var cardsHTML = vagas.map(montarCardVaga).join('');                               //Vaga
  area.innerHTML = '<div class="grade-resultados">' + cardsHTML + '</div>';
});


// --- Reserva de vaga ---
function reservar(botao) {
  botao.outerHTML = '<p class="reserva-confirmada">✅ Reserva confirmada! Seu QR Code será enviado por e-mail.</p>';
}


// --- Formulário de contato ---
document.getElementById('formContato').addEventListener('submit', function (e) {
  e.preventDefault();

  var nome     = document.getElementById('nome').value.trim();
  var email    = document.getElementById('email').value.trim();
  var mensagem = document.getElementById('mensagem').value.trim();
  var sucesso  = document.getElementById('formSucesso');

  if (!nome || !email || !mensagem) {
    alert('Por favor, preencha todos os campos.');
    return;
  }

  sucesso.style.display = 'block';
  this.reset();
});