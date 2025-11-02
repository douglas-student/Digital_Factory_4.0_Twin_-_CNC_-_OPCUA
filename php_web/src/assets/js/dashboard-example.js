// dashboard.js

// --- 1. Inicialização dos Gráficos ---

// Estrutura de dados simulada para os gráficos
let dataStatus = {
    labels: [], // Horários (eixos X)
    datasets: [
        { label: 'RUNNING', data: [], borderColor: '#28a745', fill: false, tension: 0.1, borderWidth: 2 },
        { label: 'IDLE', data: [], borderColor: '#ffc107', fill: false, tension: 0.1, borderWidth: 2 },
        { label: 'ALARM', data: [], borderColor: '#dc3545', fill: false, tension: 0.1, borderWidth: 2 }
    ]
};

let dataProducao = {
    labels: [],
    datasets: [
        { label: 'Produção Total Acumulada', data: [], borderColor: '#17a2b8', backgroundColor: 'rgba(23, 162, 184, 0.2)', fill: true, tension: 0.2 }
    ]
};

// Estrutura para 5 alarmes distintos
let alarmesDistintos = ['E101', 'E205', 'F303', 'M110', 'Z999'];
let dataAlarme = {
    labels: [],
    datasets: alarmesDistintos.map((alarme, index) => ({
        label: alarme,
        data: [],
        borderColor: `hsl(${index * 72}, 70%, 50%)`, // Cores distintas geradas via HSL
        fill: false,
        tension: 0.1,
        borderWidth: 2
    }))
};


// Opções de configuração base para gráficos de linha
const optionsBase = {
    responsive: true,
    maintainAspectRatio: false,
    scales: {
        y: {
            beginAtZero: true
        }
    }
};

// Inicializa o Status Chart
const statusChart = new Chart(
    document.getElementById('statusChart'),
    { type: 'line', data: dataStatus, options: optionsBase }
);

// Inicializa o Producao Chart
const producaoChart = new Chart(
    document.getElementById('producaoChart'),
    { type: 'line', data: dataProducao, options: optionsBase }
);

// Inicializa o Alarme Chart
const alarmeChart = new Chart(
    document.getElementById('alarmeChart'),
    { type: 'line', data: dataAlarme, options: optionsBase }
);


// --- 2. Função de Atualização Dinâmica ---

// Variáveis para simular dados
let totalPecasProduzidas = 0;
let lastStatusCounts = { RUNNING: 0, IDLE: 0, ALARM: 0 };
let lastAlarmeCounts = {};

// Função para gerar um novo ponto de dado e atualizar os gráficos
function adicionarNovoPonto() {
    const agora = new Date();
    const horaFormatada = agora.toLocaleTimeString('pt-BR');

    // 1. Simulação de Produção
    const pecasIncremento = Math.floor(Math.random() * 5) + 1; // Produz entre 1 e 5 peças
    totalPecasProduzidas += pecasIncremento;
    
    // 2. Simulação de Status (Percentual de máquinas)
    const numMaquinas = 3;
    const running = Math.floor(Math.random() * numMaquinas);
    const idle = Math.floor(Math.random() * (numMaquinas - running));
    const alarm = numMaquinas - running - idle;
    
    // 3. Simulação de Alarmes (Contagem de ocorrências)
    const novoAlarmeCounts = {};
    alarmesDistintos.forEach(alarme => {
        novoAlarmeCounts[alarme] = Math.max(0, lastAlarmeCounts[alarme] + (Math.random() > 0.6 ? 1 : -1));
    });
    lastAlarmeCounts = novoAlarmeCounts;


    // --- 4. Atualiza os KPIs ---
    document.getElementById('kpi-producao').textContent = totalPecasProduzidas.toLocaleString();
    
    // Ocioso (simulado como percentual de IDLE em relação ao total)
    document.getElementById('kpi-idle').textContent = `${((idle / numMaquinas) * 100).toFixed(0)}%`;
    
    // Alarmes Ativos (simulado como o número de alarmes distintos acima de 0)
    const alarmesAtivosCount = Object.values(lastAlarmeCounts).filter(count => count > 0).length;
    document.getElementById('kpi-alarmes').textContent = alarmesAtivosCount;


    // --- 5. Adiciona dados aos Gráficos ---

    // Adiciona o novo label de tempo
    dataStatus.labels.push(horaFormatada);
    dataProducao.labels.push(horaFormatada);
    dataAlarme.labels.push(horaFormatada);
    
    // Gráfico de Status (Contagem de máquinas em cada estado)
    dataStatus.datasets[0].data.push(running);
    dataStatus.datasets[1].data.push(idle);
    dataStatus.datasets[2].data.push(alarm);

    // Gráfico de Produção
    dataProducao.datasets[0].data.push(totalPecasProduzidas);

    // Gráfico de Alarmes
    dataAlarme.datasets.forEach(dataset => {
        dataset.data.push(lastAlarmeCounts[dataset.label]);
    });


    // --- 6. Gerencia o tamanho do histórico (Mantém os últimos 15 pontos) ---
    const limitePontos = 15;
    if (dataStatus.labels.length > limitePontos) {
        dataStatus.labels.shift();
        dataProducao.labels.shift();
        dataAlarme.labels.shift();
        
        dataStatus.datasets.forEach(dataset => dataset.data.shift());
        dataProducao.datasets.forEach(dataset => dataset.data.shift());
        dataAlarme.datasets.forEach(dataset => dataset.data.shift());
    }

    // --- 7. Atualiza os Gráficos na tela ---
    statusChart.update();
    producaoChart.update();
    alarmeChart.update();
}


// Inicializa a contagem dos alarmes
alarmesDistintos.forEach(alarme => {
    lastAlarmeCounts[alarme] = 0;
});

// Executa a primeira atualização e inicia o loop de simulação
adicionarNovoPonto(); 
setInterval(adicionarNovoPonto, 5000); // Atualiza a cada 5 segundos