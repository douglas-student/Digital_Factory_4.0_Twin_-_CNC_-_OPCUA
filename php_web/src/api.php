<?php
    // Inclui o arquivo de conexão com o banco de dados
    require_once 'includes/db_connection.php';

    // Define o cabeçalho para indicar que a resposta é JSON
    header('Content-Type: application/json');

    $dados_agrupados = [];

    try {
        // Query para buscar todos os registros ordenados
        $query = "
            SELECT *
            FROM dados_monitoramento
            ORDER BY maquina_id ASC, timestamp DESC;
        ";
        
        $stmt = $conn->prepare($query);
        $stmt->execute();
        $registros_completos = $stmt->fetchAll(PDO::FETCH_ASSOC);

        // Processa os registros para agrupar por máquina
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
    } catch (PDOException $e) {
        // Se a tabela não existir, retorna uma resposta vazia
        if ($e->getCode() === '42P01') {
            echo json_encode(['erro' => 'Tabela nao encontrada.']);
            exit;
        } else {
            die(json_encode(['erro' => 'Erro ao buscar dados: ' . $e->getMessage()]));
        }
    }
    
    // Retorna os dados em formato JSON
    echo json_encode($dados_agrupados);
?>