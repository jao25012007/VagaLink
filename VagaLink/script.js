// ============================================
// VagaLink – script.js
// ============================================

// --- Ano atual no footer ---
document.getElementById('anoAtual').textContent = new Date().getFullYear();

// --- Menu hamburguer (mobile) ---
var btnMenu = document.getElementById('menuToggle');
var nav     = document.getElementById('mainNav');

btnMenu.addEventListener('click', function() {
  nav.classList.toggle('aberto');
});

// Fecha o menu ao clicar em qualquer link do nav
var links = document.querySelectorAll('.nav-link');
for (var i = 0; i < links.length; i++) {
  links[i].addEventListener('click', function() {
    nav.classList.remove('aberto');
  });
}

// --- Vagas fictícias ---
var vagas = [
  { nome: 'Garagem Central',       endereco: 'Rua das Flores, 142 – Centro',     preco: 'R$ 8/hora',  tipo: 'coberta', avaliacao: '⭐ 4.9' },
  { nome: 'Estacionamento Premium', endereco: 'Av. Brasil, 500 – Centro',          preco: 'R$ 10/hora', tipo: 'coberta', avaliacao: '⭐ 4.8' },
  { nome: 'Vaga Ana Silva',         endereco: 'Rua Pioneiro, 88 – Zona 7',         preco: 'R$ 6/hora',  tipo: 'aberta',  avaliacao: '⭐ 4.7' },
  { nome: 'Garagem do João',        endereco: 'Rua Paraíba, 210 – Jardim Alvorada',preco: 'R$ 5/hora',  tipo: 'aberta',  avaliacao: '⭐ 4.6' },
  { nome: 'Vaga Segura Express',    endereco: 'Av. Colombo, 1200 – Centro',        preco: 'R$ 9/hora',  tipo: 'coberta', avaliacao: '⭐ 5.0' },
];

// --- Busca de vagas ---
document.getElementById('btnBuscar').addEventListener('click', function() {
  var cidade = document.getElementById('cidade').value;
  var bairro = document.getElementById('bairro').value.trim();
  var data   = document.getElementById('data').value;
  var area   = document.getElementById('resultados');

  // Validação simples
  if (!cidade || !bairro || !data) {
    area.innerHTML = '<p class="resultados-placeholder">⚠️ Preencha todos os campos antes de buscar.</p>';
    return;
  }

  // Monta o grid de cards
  var html = '<div class="resultados-grid">';

  for (var i = 0; i < vagas.length; i++) {
    var v = vagas[i];
    html += '<div class="vaga-card">';
    html +=   '<div class="vaga-card-header">';
    html +=     '<span class="vaga-nome">' + v.nome + '</span>';
    html +=     '<span class="vaga-tipo ' + v.tipo + '">' + v.tipo + '</span>';
    html +=   '</div>';
    html +=   '<p class="vaga-endereco">📍 ' + v.endereco + '</p>';
    html +=   '<div class="vaga-footer">';
    html +=     '<span class="vaga-preco">' + v.preco + '</span>';
    html +=     '<span class="vaga-avaliacao">' + v.avaliacao + '</span>';
    html +=   '</div>';
    html +=   '<button class="btn-reservar" onclick="reservar(this)">Reservar</button>';
    html += '</div>';
  }

  html += '</div>';
  area.innerHTML = html;
});

// --- Reserva de vaga ---
function reservar(botao) {
  // Substitui o botão pela mensagem de confirmação
  botao.outerHTML = '<p class="reserva-confirmada">✅ Reserva confirmada! Seu QR Code será enviado por e-mail.</p>';
}

// --- Formulário de contato ---
document.getElementById('formContato').addEventListener('submit', function(e) {
  e.preventDefault(); // Impede o envio real (sem backend)

  var nome     = document.getElementById('nome').value.trim();
  var email    = document.getElementById('email').value.trim();
  var mensagem = document.getElementById('mensagem').value.trim();
  var sucesso  = document.getElementById('formSucesso');

  // Validação simples
  if (!nome || !email || !mensagem) {
    alert('Por favor, preencha todos os campos.');
    return;
  }

  // Exibe mensagem de sucesso e limpa o formulário
  sucesso.style.display = 'block';
  this.reset();
});