// update_dashboard.js

// Função para formatar a hora (ex: 14:05:30)
function formatarHora(timestamp) {
    const data = new Date(timestamp);
    const horas = String(data.getHours()).padStart(2, '0');
    const minutos = String(data.getMinutes()).padStart(2, '0');
    const segundos = String(data.getSeconds()).padStart(2, '0');
    return `${horas}:${minutos}:${segundos}`;
}

// Função para renderizar as tabelas de histórico
function renderizarTabela(dados, tipo) {
    let tabelaHtml = '';
    
    // Define os cabeçalhos da tabela com base no tipo
    if (tipo === 'producao') {
        tabelaHtml = `
            <table class="table table-striped">
                <thead>
                    <tr>
                        <th>Produção</th>
                        <th>Hora</th>
                    </tr>
                </thead>
                <tbody>
        `;
        dados.forEach(registro => {
            tabelaHtml += `
                <tr>
                    <td>${registro.producao_total}</td>
                    <td>${formatarHora(registro.timestamp)}</td>
                </tr>
            `;
        });
    } else if (tipo === 'status') {
        tabelaHtml = `
            <table class="table table-striped">
                <thead>
                    <tr>
                        <th>Status</th>
                        <th>Hora</th>
                    </tr>
                </thead>
                <tbody>
        `;
        dados.forEach(registro => {
            tabelaHtml += `
                <tr>
                    <td>${registro.status}</td>
                    <td>${formatarHora(registro.timestamp)}</td>
                </tr>
            `;
        });
    } else if (tipo === 'alarmes') {
        tabelaHtml = `
            <table class="table table-striped">
                <thead>
                    <tr>
                        <th>Alarme</th>
                        <th>Hora</th>
                    </tr>
                </thead>
                <tbody>
        `;
        dados.forEach(registro => {
            tabelaHtml += `
                <tr>
                    <td>${registro.alarmes_ativos}</td>
                    <td>${formatarHora(registro.timestamp)}</td>
                </tr>
            `;
        });
    }

    tabelaHtml += `
            </tbody>
        </table>
    `;
    return tabelaHtml;
}

// Função principal que busca e atualiza os dados
async function atualizarDashboard() {
    console.log('Buscando dados da API...');
    try {
        const response = await fetch('api.php');
        const dados = await response.json();
        
        // Verifica se a resposta contém um erro do banco de dados
        if (dados.erro) {
            console.error('Erro da API:', dados.erro);
            const containerMaquinas = document.getElementById('maquinas-container');
            containerMaquinas.innerHTML = `
                <div class="loading-message text-center">
                    <h2>Aguardando dados do banco de dados...</h2>
                    <p>A primeira inicialização pode levar alguns segundos.</p>
                </div>
            `;
            return;
        }

        const containerMaquinas = document.getElementById('maquinas-container');
        containerMaquinas.innerHTML = ''; // Limpa o conteúdo anterior

        for (const maquinaId in dados) {
            if (dados.hasOwnProperty(maquinaId)) {
                const maquina = dados[maquinaId];
                const lastData = maquina.last_data;

                // Garante que o valor de posicao_x é um número antes de usar toFixed
                const posicaoX = typeof lastData.posicao_x === 'number' ? lastData.posicao_x.toFixed(2) : '0.00';

                const cardHtml = `
                    <div class="col">
                        <div class="card maquina-card status-${lastData.status.toLowerCase()}">
                            <div class="card-body text-center">
                                <h2 class="card-title">${maquinaId}</h2>
                                <div class="dados">
                                    <p class="card-text"><strong>Status:</strong> <span class="status-text">${lastData.status}</span></p>
                                    <p class="card-text"><strong>Produção Total:</strong> ${lastData.producao_total}</p>
                                    <p class="card-text"><strong>Posição (X):</strong> ${posicaoX}</p>
                                    <p class="card-text"><strong>Alarmes:</strong> ${lastData.alarmes_ativos || 'Nenhum'}</p>
                                </div>

                                <div class="accordion mt-3" id="accordion-${maquinaId}">

                                    <div class="accordion-item bg-success bg-gradient">
                                        <h2 class="accordion-header">
                                            <button class="accordion-button collapsed bg-white bg-gradient bg-opacity-50"" type="button" data-bs-toggle="collapse" data-bs-target="#producao-${maquinaId}">
                                                Histórico de Produção
                                            </button>
                                        </h2>
                                        <div id="producao-${maquinaId}" class="accordion-collapse collapse" data-bs-parent="#accordion-${maquinaId}">
                                            <div class="accordion-body">
                                                ${renderizarTabela(maquina.producao, 'producao')}
                                            </div>
                                        </div>
                                    </div>

                                    <div class="accordion-item bg-warning bg-gradient">
                                        <h2 class="accordion-header">
                                            <button class="accordion-button collapsed bg-white bg-gradient bg-opacity-50"" type="button" data-bs-toggle="collapse" data-bs-target="#status-${maquinaId}">
                                                Histórico de Status
                                            </button>
                                        </h2>
                                        <div id="status-${maquinaId}" class="accordion-collapse collapse" data-bs-parent="#accordion-${maquinaId}">
                                            <div class="accordion-body">
                                                ${renderizarTabela(maquina.status, 'status')}
                                            </div>
                                        </div>
                                    </div>
                                    
                                    <div class="accordion-item bg-danger bg-gradient">
                                        <h2 class="accordion-header">
                                            <button class="accordion-button collapsed bg-white bg-gradient bg-opacity-50"" type="button" data-bs-toggle="collapse" data-bs-target="#alarmes-${maquinaId}">
                                                Histórico de Alarmes
                                            </button>
                                        </h2>
                                        <div id="alarmes-${maquinaId}" class="accordion-collapse collapse" data-bs-parent="#accordion-${maquinaId}">
                                            <div class="accordion-body">
                                                ${renderizarTabela(maquina.alarmes, 'alarmes')}
                                            </div>
                                        </div>
                                    </div>
                                    
                                </div>
                            </div>
                        </div>
                    </div>
                `;
                containerMaquinas.innerHTML += cardHtml;
            }
        }

    } catch (error) {
        console.error('Erro ao buscar dados da API:', error);
    }
}

// Atualiza o dashboard a cada 60 segundos
setInterval(atualizarDashboard, 60000);

// Executa a função na primeira carga da página
document.addEventListener('DOMContentLoaded', atualizarDashboard);