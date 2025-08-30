<?php
    // Inclui o arquivo de conexão com o banco de dados
    require_once 'includes/db_connection.php';

    $dados_agrupados = [];
    $erro_banco = false;

    try {
        $query = "
            SELECT *
            FROM dados_monitoramento
            ORDER BY maquina_id ASC, timestamp DESC;
        ";
        
        $stmt = $conn->prepare($query);
        $stmt->execute();
        $registros_completos = $stmt->fetchAll(PDO::FETCH_ASSOC);

        $dados_agrupados = [];
        foreach ($registros_completos as $registro) {
            $maquina_id = $registro['maquina_id'];

            if (!isset($dados_agrupados[$maquina_id])) {
                $dados_agrupados[$maquina_id] = [
                    'last_data' => $registro,
                    'producao' => [],
                    'status' => [],
                    'alarmes' => []
                ];
            }

            // Agrupa os dados de Produção (últimos 10 distintos)
            if (count($dados_agrupados[$maquina_id]['producao']) < 10) {
                $last_value = end($dados_agrupados[$maquina_id]['producao']);
                if ($registro['producao_total'] > 0 && ($last_value === false || $last_value['producao_total'] != $registro['producao_total'])) {
                    $dados_agrupados[$maquina_id]['producao'][] = $registro;
                }
            }

            // Agrupa os dados de Status (últimos 10 distintos)
            if (count($dados_agrupados[$maquina_id]['status']) < 10) {
                $last_value = end($dados_agrupados[$maquina_id]['status']);
                if ($last_value === false || $last_value['status'] != $registro['status']) {
                    $dados_agrupados[$maquina_id]['status'][] = $registro;
                }
            }
            
            // Agrupa os dados de Alarmes (últimos 10 distintos)
            if (count($dados_agrupados[$maquina_id]['alarmes']) < 10) {
                $last_value = end($dados_agrupados[$maquina_id]['alarmes']);
                if (!empty($registro['alarmes_ativos']) && ($last_value === false || $last_value['alarmes_ativos'] != $registro['alarmes_ativos'])) {
                    $dados_agrupados[$maquina_id]['alarmes'][] = $registro;
                }
            }
        }
        
        // Inverte os arrays para que os dados mais recentes fiquem no topo
        foreach ($dados_agrupados as $maquina_id => $dados) {
            $dados_agrupados[$maquina_id]['producao'] = array_reverse($dados['producao']);
            $dados_agrupados[$maquina_id]['status'] = array_reverse($dados['status']);
            $dados_agrupados[$maquina_id]['alarmes'] = array_reverse($dados['alarmes']);
        }

    } catch (PDOException $e) {
        if ($e->getCode() === '42P01') {
            $erro_banco = true;
        } else {
            die("Erro ao buscar dados: " . $e->getMessage());
        }
    }
?>

<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Monitoramento de Fábrica 4.0</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="assets/css/style.css">
</head>
<body>
    <header class="bg-primary text-white text-center py-3">
        <h1>Monitoramento de Fábrica 4.0</h1>
    </header>

    <main class="container py-4">
        <?php if ($erro_banco): ?>
            <div class="loading-message text-center">
                <h2>Aguardando dados do banco de dados...</h2>
                <p>A primeira inicialização pode levar alguns segundos.</p>
            </div>
        <?php else: ?>
            <div class="row row-cols-1 row-cols-md-3 g-4">
                <?php foreach ($dados_agrupados as $maquina_id => $dados_maquina): ?>
                <div class="col">
                    <div class="card maquina-card status-<?php echo strtolower($dados_maquina['last_data']['status']); ?>">
                        <div class="card-body text-center">
                            <h2 class="card-title"><?php echo htmlspecialchars($maquina_id); ?></h2>
                            <div class="dados">
                                <p class="card-text"><strong>Status:</strong> <span class="status-text"><?php echo htmlspecialchars($dados_maquina['last_data']['status']); ?></span></p>
                                <p class="card-text"><strong>Produção Total:</strong> <?php echo htmlspecialchars($dados_maquina['last_data']['producao_total']); ?></p>
                                <p class="card-text"><strong>Posição (X):</strong> <?php echo number_format($dados_maquina['last_data']['posicao_x'], 2); ?></p>
                                <p class="card-text"><strong>Alarmes:</strong> <?php echo htmlspecialchars($dados_maquina['last_data']['alarmes_ativos']); ?></p>
                            </div>

                            <div class="accordion mt-3 bg-info bg-gradient" id="accordion-<?php echo htmlspecialchars($maquina_id); ?>">

                                <div class="accordion-item bg-success bg-gradient">
                                    <h2 class="accordion-header">
                                        <button class="accordion-button collapsed bg-white bg-gradient bg-opacity-50" type="button" data-bs-toggle="collapse" data-bs-target="#producao-<?php echo htmlspecialchars($maquina_id); ?>">
                                            Histórico de Produção
                                        </button>
                                    </h2>
                                    <div id="producao-<?php echo htmlspecialchars($maquina_id); ?>" class="accordion-collapse collapse" data-bs-parent="#accordion-<?php echo htmlspecialchars($maquina_id); ?>">
                                        <div class="accordion-body">
                                            <table class="table table-striped">
                                                <thead>
                                                    <tr>
                                                        <th>Produção</th>
                                                        <th>Hora</th>
                                                    </tr>
                                                </thead>
                                                <tbody>
                                                    <?php foreach ($dados_maquina['producao'] as $registro): ?>
                                                    <tr>
                                                        <td><?php echo htmlspecialchars($registro['producao_total']); ?></td>
                                                        <td><?php echo htmlspecialchars(date('H:i:s', strtotime($registro['timestamp']))); ?></td>
                                                    </tr>
                                                    <?php endforeach; ?>
                                                </tbody>
                                            </table>
                                        </div>
                                    </div>
                                </div>

                                <div class="accordion-item bg-warning bg-gradient">
                                    <h2 class="accordion-header">
                                        <button class="accordion-button collapsed bg-white bg-gradient bg-opacity-50" type="button" data-bs-toggle="collapse" data-bs-target="#status-<?php echo htmlspecialchars($maquina_id); ?>">
                                            Histórico de Status
                                        </button>
                                    </h2>
                                    <div id="status-<?php echo htmlspecialchars($maquina_id); ?>" class="accordion-collapse collapse" data-bs-parent="#accordion-<?php echo htmlspecialchars($maquina_id); ?>">
                                        <div class="accordion-body">
                                            <table class="table table-striped">
                                                <thead>
                                                    <tr>
                                                        <th>Status</th>
                                                        <th>Hora</th>
                                                    </tr>
                                                </thead>
                                                <tbody>
                                                    <?php foreach ($dados_maquina['status'] as $registro): ?>
                                                    <tr>
                                                        <td><?php echo htmlspecialchars($registro['status']); ?></td>
                                                        <td><?php echo htmlspecialchars(date('H:i:s', strtotime($registro['timestamp']))); ?></td>
                                                    </tr>
                                                    <?php endforeach; ?>
                                                </tbody>
                                            </table>
                                        </div>
                                    </div>
                                </div>

                                <div class="accordion-item bg-danger bg-gradient text-white">
                                    <h2 class="accordion-header">
                                        <button class="accordion-button collapsed bg-black bg-white text-black bg-opacity-50" type="button" data-bs-toggle="collapse" data-bs-target="#alarmes-<?php echo htmlspecialchars($maquina_id); ?>">
                                            Histórico de Alarmes
                                        </button>
                                    </h2>
                                    <div id="alarmes-<?php echo htmlspecialchars($maquina_id); ?>" class="accordion-collapse collapse" data-bs-parent="#accordion-<?php echo htmlspecialchars($maquina_id); ?>">
                                        <div class="accordion-body">
                                            <table class="table table-striped">
                                                <thead>
                                                    <tr>
                                                        <th>Alarme</th>
                                                        <th>Hora</th>
                                                    </tr>
                                                </thead>
                                                <tbody>
                                                    <?php foreach ($dados_maquina['alarmes'] as $registro): ?>
                                                    <tr>
                                                        <td><?php echo htmlspecialchars($registro['alarmes_ativos']); ?></td>
                                                        <td><?php echo htmlspecialchars(date('H:i:s', strtotime($registro['timestamp']))); ?></td>
                                                    </tr>
                                                    <?php endforeach; ?>
                                                </tbody>
                                            </table>
                                        </div>
                                    </div>
                                </div>

                            </div>
                        </div>
                    </div>
                </div>
                <?php endforeach; ?>
            </div>
        <?php endif; ?>
    </main>

    <footer class="bg-primary text-white text-center py-3 mt-4">
        <p>Projeto de Gêmeo Digital - Indústria 4.0</p>
    </footer>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        // Recarrega a página a cada 5 segundos para atualizar os dados
        setTimeout(function(){
            window.location.reload(1);
        }, 15000);
    </script>
</body>
</html>