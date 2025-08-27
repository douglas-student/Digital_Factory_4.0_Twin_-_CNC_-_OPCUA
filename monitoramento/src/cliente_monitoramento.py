# cliente_monitoramento.py (Versão Corrigida)
import asyncio
from asyncua import Client
import time

# Esta função irá se conectar a um único servidor OPC-UA (um CNC)
async def coletar_dados_de_cnc(endpoint_url):
    """
    Conecta a um servidor OPC-UA e coleta os dados de uma máquina CNC.
    """
    try:
        # 1. Conectar ao servidor
        async with Client(url=endpoint_url) as client:
            print(f"Conectado com sucesso ao servidor {endpoint_url}")

            # 2. Navegar no espaço de endereçamento para encontrar as variáveis
            # Extrai o nome do serviço (ex: cnc_simulador_1) da URL
            nome_servico = endpoint_url.split('/')[2].split(':')[0]
            uri = f"http://example.org/{nome_servico}" 
            idx = await client.get_namespace_index(uri)

            # Encontrar os nós das variáveis
            maquina_node = await client.nodes.objects.get_child([f"{idx}:{nome_servico}"])
            var_status = await maquina_node.get_child(f"{idx}:Status")
            var_producao = await maquina_node.get_child(f"{idx}:ProducaoTotal")
            var_posicao_x = await maquina_node.get_child(f"{idx}:PosicaoX")
            var_alarmes = await maquina_node.get_child(f"{idx}:AlarmesAtivos")

            # 3. Ler os valores das variáveis
            status = await var_status.read_value()
            producao_total = await var_producao.read_value()
            posicao_x = await var_posicao_x.read_value()
            alarmes_ativos = await var_alarmes.read_value()

            # 4. Processar e exibir os dados
            dados = {
                'maquina_id': nome_servico,
                'status': status,
                'producao_total': producao_total,
                'posicao_x': posicao_x,
                'alarmes_ativos': alarmes_ativos
            }
            return dados

    except Exception as e:
        print(f"Erro ao conectar ou coletar dados do {endpoint_url}: {e}")
        return None

# Esta função será o loop principal que gerencia todos os clientes
async def main_monitoramento(lista_de_endpoints):
    """
    Função principal que gerencia a coleta de dados de múltiplos CNCs.
    """
    while True:
        print("--------------------")
        print("Iniciando nova rodada de coleta de dados...")
        
        # Cria uma lista de tarefas assíncronas para cada CNC
        tasks = [coletar_dados_de_cnc(endpoint) for endpoint in lista_de_endpoints]
        
        # Executa todas as tarefas de coleta em paralelo
        resultados = await asyncio.gather(*tasks)
        
        # Processa e salva os resultados no banco de dados (próxima etapa)
        for resultado in resultados:
            if resultado:
                print(f"Dados Coletados: {resultado}")
                # Aqui você chamará a função para salvar no banco de dados
                # salvar_no_banco(resultado)
        
        print("Rodada de coleta finalizada. Aguardando 10 segundos...")
        await asyncio.sleep(10) # Coleta a cada 10 segundos

# Para rodar o script diretamente:
if __name__ == "__main__":
    import sys
    # A lista de endpoints virá do script "Starter-Project.py"
    # Exemplo: ["opc.tcp://cnc1:4840/freeopcua/server/", "opc.tcp://cnc2:4840/freeopcua/server/"]
    endpoints = sys.argv[1:] 
    if not endpoints:
        print("Por favor, forneça os endpoints dos servidores como argumentos.")
    else:
        asyncio.run(main_monitoramento(endpoints))