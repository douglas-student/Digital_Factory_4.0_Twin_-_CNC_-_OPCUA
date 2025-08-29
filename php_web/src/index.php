<?php
    // Inclui o arquivo de conexão com o banco de dados
    require_once 'includes/db_connection.php';

    // Query para buscar os dados mais recentes de cada máquina
    // Nota: Em uma aplicação real, você usaria uma query mais otimizada.
    $query = "
        SELECT DISTINCT ON (maquina_id) *
        FROM dados_monitoramento
        ORDER BY maquina_id, timestamp DESC;
    ";

    try {
        $stmt = $conn->prepare($query);
        $stmt->execute();
        $dados_maquinas = $stmt->fetchAll(PDO::FETCH_ASSOC);
    } catch (PDOException $e) {
        die("Erro ao buscar dados: " . $e->getMessage());
    }
?>

<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Monitoramento de Fábrica 4.0</title>
    <link rel="stylesheet" href="assets/css/style.css">
</head>
<body>
    <header>
        <h1>Monitoramento de Fábrica 4.0</h1>
    </header>

    <main>
        <div class="maquinas-container">
            <?php foreach ($dados_maquinas as $maquina): ?>
            <div class="maquina-card status-<?php echo strtolower($maquina['status']); ?>">
                <h2><?php echo htmlspecialchars($maquina['maquina_id']); ?></h2>
                <div class="dados">
                    <p><strong>Status:</strong> <span class="status-text"><?php echo htmlspecialchars($maquina['status']); ?></span></p>
                    <p><strong>Produção Total:</strong> <?php echo htmlspecialchars($maquina['producao_total']); ?></p>
                    <p><strong>Posição (X):</strong> <?php echo number_format($maquina['posicao_x'], 2); ?></p>
                    <p><strong>Alarmes:</strong> <?php echo htmlspecialchars($maquina['alarmes_ativos']); ?></p>
                </div>
            </div>
            <?php endforeach; ?>
        </div>
    </main>

    <footer>
        <p>Projeto: Simulação de Fábrica 4.0 com Docker e OPC-UA</p>
    </footer>

    <script>
        // Recarrega a página a cada 5 segundos para atualizar os dados
        setTimeout(function(){
            window.location.reload(1);
        }, 5000);
    </script>
</body>
</html>