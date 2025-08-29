# cliente_monitoramento.py (Versão Final)
import asyncio
from asyncua import Client
import time
import asyncpg
import os
import json

# Funções de Banco de Dados
async def conectar_ao_banco():
    """Conecta ao banco de dados PostgreSQL usando variáveis de ambiente."""
    try:
        conn = await asyncpg.connect(
            user=os.environ.get('POSTGRES_USER'),
            password=os.environ.get('POSTGRES_PASSWORD'),
            database=os.environ.get('POSTGRES_DB'),
            host=os.environ.get('POSTGRES_HOST')
        )
        print("Conectado com sucesso ao banco de dados!")
        return conn
    except Exception as e:
        print(f"Erro ao conectar ao banco de dados: {e}")
        return None

async def criar_tabela(conn):
    """Cria a tabela dados_monitoramento se ela não existir."""
    await conn.execute('''
        CREATE TABLE IF NOT EXISTS dados_monitoramento (
            id SERIAL PRIMARY KEY,
            maquina_id VARCHAR(50),
            status VARCHAR(20),
            producao_total INTEGER,
            posicao_x FLOAT,
            alarmes_ativos TEXT,
            timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        );
    ''')

async def inserir_dados(conn, dados):
    """Insere um novo registro na tabela dados_monitoramento."""
    try:
        await conn.execute('''
            INSERT INTO dados_monitoramento (maquina_id, status, producao_total, posicao_x, alarmes_ativos)
            VALUES ($1, $2, $3, $4, $5);
        ''', dados['maquina_id'], dados['status'], dados['producao_total'], dados['posicao_x'], dados['alarmes_ativos'])
    except Exception as e:
        print(f"Erro ao inserir dados: {e}")

# Função de Coleta de Dados OPC-UA
async def coletar_dados_de_cnc(endpoint_url):
    """Conecta a um servidor OPC-UA e coleta os dados de uma máquina CNC."""
    try:
        async with Client(url=endpoint_url) as client:
            print(f"Conectado com sucesso ao servidor {endpoint_url}")
            nome_servico = endpoint_url.split('/')[2].split(':')[0]
            uri = f"http://example.org/{nome_servico}" 
            idx = await client.get_namespace_index(uri)
            maquina_node = await client.nodes.objects.get_child([f"{idx}:{nome_servico}"])
            var_status = await maquina_node.get_child(f"{idx}:Status")
            var_producao = await maquina_node.get_child(f"{idx}:ProducaoTotal")
            var_posicao_x = await maquina_node.get_child(f"{idx}:PosicaoX")
            var_alarmes = await maquina_node.get_child(f"{idx}:AlarmesAtivos")
            status = await var_status.read_value()
            producao_total = await var_producao.read_value()
            posicao_x = await var_posicao_x.read_value()
            alarmes_ativos = await var_alarmes.read_value()
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

# Função Principal
async def main_monitoramento(lista_de_endpoints):
    """Função principal que gerencia a coleta de dados e a gravação no banco de dados."""
    conn = await conectar_ao_banco()
    if conn:
        await criar_tabela(conn)
        
        while True:
            print("--------------------")
            print("Iniciando nova rodada de coleta de dados...")
            
            tasks = [coletar_dados_de_cnc(endpoint) for endpoint in lista_de_endpoints]
            resultados = await asyncio.gather(*tasks)
            
            for resultado in resultados:
                if resultado:
                    await inserir_dados(conn, resultado)
                    print(f"Dados Coletados e Salvos: {resultado['maquina_id']}")
            
            print("Rodada de coleta finalizada. Aguardando 10 segundos...")
            await asyncio.sleep(10)

if __name__ == "__main__":
    import sys
    endpoints = sys.argv[1:] 
    if not endpoints:
        print("Por favor, forneça os endpoints dos servidores como argumentos.")
    else:
        # Acesso às variáveis de ambiente diretamente pelo script
        os.environ['POSTGRES_USER'] = 'user'
        os.environ['POSTGRES_PASSWORD'] = 'password'
        os.environ['POSTGRES_DB'] = 'fabrica'
        os.environ['POSTGRES_HOST'] = 'banco_de_dados'
        asyncio.run(main_monitoramento(endpoints))