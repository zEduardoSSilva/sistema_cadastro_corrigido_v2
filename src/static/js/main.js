// Funções JavaScript para o Sistema de Cadastro

// Função para exibir toast
function showToast(title, message, type) {
    const toast = `
        <div class="toast align-items-center text-white bg-${type} border-0" role="alert" aria-live="assertive" aria-atomic="true">
            <div class="d-flex">
                <div class="toast-body">
                    <strong>${title}</strong> ${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
            </div>
        </div>
    `;
    
    $('.toast-container').append(toast);
    var toastEl = $('.toast').last();
    var bsToast = new bootstrap.Toast(toastEl, { autohide: true, delay: 5000 });
    bsToast.show();
    
    // Remover toast após fechamento
    toastEl.on('hidden.bs.toast', function() {
        $(this).remove();
    });
}

// Função para formatar data
function formatarData(dataStr) {
    if (!dataStr) return '-';
    const data = new Date(dataStr);
    return data.toLocaleDateString('pt-BR');
}

// Função para formatar moeda
function formatarMoeda(valor) {
    return parseFloat(valor).toLocaleString('pt-BR', {
        style: 'currency',
        currency: 'BRL'
    });
}

// Função para verificar status de conexão
function verificarStatusConexao() {
    $.ajax({
        url: '/test_connection',
        type: 'GET',
        success: function(response) {
            atualizarStatusConexao(response);
        },
        error: function() {
            atualizarStatusConexao({
                status: false,
                message: 'Erro ao verificar conexão'
            });
        }
    });
}

// Função para atualizar indicadores de status de conexão
function atualizarStatusConexao(status) {
    // Status na navbar
    const statusMini = $('.connection-status-mini span');
    
    if (status.status) {
        statusMini.removeClass('bg-danger').addClass('bg-success');
        statusMini.html('<i class="fas fa-check-circle me-1"></i>Conectado');
    } else {
        statusMini.removeClass('bg-success').addClass('bg-danger');
        statusMini.html('<i class="fas fa-exclamation-circle me-1"></i>Desconectado');
    }
    
    // Status na página inicial (se existir)
    const statusLarge = $('.connection-status-large .alert');
    if (statusLarge.length > 0) {
        if (status.status) {
            statusLarge.removeClass('alert-danger').addClass('alert-success');
            statusLarge.find('i').removeClass('fa-exclamation-circle').addClass('fa-check-circle');
            statusLarge.find('strong').text('Banco conectado');
        } else {
            statusLarge.removeClass('alert-success').addClass('alert-danger');
            statusLarge.find('i').removeClass('fa-check-circle').addClass('fa-exclamation-circle');
            statusLarge.find('strong').text('Banco desconectado');
        }
    }
}

// Função para carregar dicas aleatórias
function carregarDicaAleatoria(elementId, dicas) {
    const dicaAleatoria = dicas[Math.floor(Math.random() * dicas.length)];
    $(`#${elementId}`).text(dicaAleatoria);
}

// Função para validar formulário
function validarFormulario(formId, campos) {
    let valido = true;
    
    campos.forEach(campo => {
        const elemento = $(`#${formId} #${campo}`);
        if (elemento.prop('required') && !elemento.val()) {
            elemento.addClass('is-invalid');
            valido = false;
        } else {
            elemento.removeClass('is-invalid');
        }
    });
    
    return valido;
}

// Função para confirmar ação
function confirmarAcao(titulo, mensagem, callback) {
    if (confirm(`${titulo}\n\n${mensagem}`)) {
        callback();
    }
}

// Verificar status de conexão ao carregar a página
$(document).ready(function() {
    verificarStatusConexao();
    
    // Verificar status a cada 30 segundos
    setInterval(verificarStatusConexao, 30000);
});
