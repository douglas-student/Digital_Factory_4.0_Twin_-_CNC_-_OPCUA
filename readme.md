# Projeto: Simulação de Fábrica 4.0 com Docker e OPC-UA

Este projeto é uma demonstração de uma arquitetura de Manufatura Inteligente e Indústria 4.0, utilizando Python e Docker. O objetivo é simular uma linha de produção com múltiplos controladores CNC e um sistema central de monitoramento, utilizando o protocolo de comunicação industrial OPC-UA.

-----

### Sumário

  * [Visão Geral da Arquitetura](https://www.google.com/search?q=%23vis%C3%A3o-geral-da-arquitetura)
  * [Estrutura de Arquivos do Projeto](https://www.google.com/search?q=%23estrutura-de-arquivos-do-projeto)
  * [Componentes do Sistema](https://www.google.com/search?q=%23componentes-do-sistema)
      * `starter-project.py`
      * `stopper-project.py`
      * `docker-compose.yml`
      * Pasta `simulador_cnc/`
      * Pasta `monitoramento/`
      * Pasta `banco_de_dados/`
  * [Lógica de Simulação](https://www.google.com/search?q=%23l%C3%B3gica-de-simula%C3%A7%C3%A3o)
      * Classe `SimuladorCNC`
      * Classe `OperadorCNC`
  * [Comunicação via OPC-UA](https://www.google.com/search?q=%23comunica%C3%A7%C3%A3o-via-opc-ua)
      * Servidor OPC-UA
      * Cliente OPC-UA
  * [Como Executar o Projeto](https://www.google.com/search?q=%23como-executar-o-projeto)

-----

### Visão Geral da Arquitetura

O sistema é composto por múltiplos serviços que se comunicam através de uma rede Docker interna, seguindo o padrão cliente-servidor para a coleta de dados.

  * **Orquestrador (`starter-project.py`)**: Ponto de entrada do sistema. É responsável por perguntar ao usuário a quantidade de simuladores CNC a serem criados e, em seguida, gerar e executar o ambiente Docker completo.
  * **Simuladores CNC**: Cada simulador é um contêiner Docker individual que atua como um **servidor OPC-UA**. Ele executa um script Python que simula o comportamento de uma máquina CNC, gerando dados como status, posições de eixos e alarmes.
  * **Sistema de Monitoramento**: Um contêiner Docker separado que funciona como um **cliente OPC-UA**. Ele se conecta a cada um dos simuladores para coletar os dados em tempo real.
  * **Banco de Dados**: Um contêiner que armazena os dados coletados pelo sistema de monitoramento.

### Estrutura de Arquivos do Projeto

A organização dos arquivos e diretórios reflete a modularidade do projeto.

```
.
├── starter_project.py
├── docker-compose.yml
├── simulador_cnc/
│   ├── Dockerfile
│   ├── src/
│   │   ├── simulador_cnc.py
│   │   └── operador_cnc.py
│   └── requirements.txt
├── monitoramento/
│   ├── Dockerfile
│   ├── src/
│   │   └── cliente_monitoramento.py
│   └── requirements.txt
└── banco_de_dados/
    └── .env
```

-----

### Componentes do Sistema

#### `starter-project.py`

Este script Python atua como o **orquestrador** do projeto. Ele é executado na máquina local (fora de um contêiner) e possui as seguintes funções:

  * Gera dinamicamente o arquivo `docker-compose.yml` com base na entrada do usuário.
  * Inicia e gerencia todos os contêineres e suas redes usando `docker-compose`.

#### `docker-compose.yml`

Este arquivo é gerado pelo `starter-project.py` e define a arquitetura da fábrica virtual. Ele configura a rede interna do Docker (`industria40_net`) e descreve os serviços:

  * `banco_de_dados`: Utiliza uma imagem oficial do PostgreSQL.
  * `monitoramento`: Constrói a imagem do cliente de monitoramento a partir do `Dockerfile` e depende do banco de dados e dos simuladores.
  * `cnc_simulador_X`: Constrói a imagem de cada simulador a partir do `Dockerfile` e expõe uma porta OPC-UA para comunicação.

#### Pasta `simulador_cnc/`

Esta pasta contém os arquivos para a construção da imagem Docker dos simuladores.

  * `Dockerfile`: Contém as instruções para construir a imagem, copiando os scripts Python e instalando as dependências.
  * `src/`: Contém os scripts Python de simulação.
      * `simulador_cnc.py`: Lógica principal de simulação e o servidor OPC-UA.
      * `operador_cnc.py`: Simula as ações de um operador humano (iniciar/parar ciclo, gerar falhas).
  * `requirements.txt`: Lista as bibliotecas Python necessárias para o simulador, incluindo `asyncua`.

#### Pasta `monitoramento/`

Esta pasta contém os arquivos para a construção da imagem Docker do cliente de monitoramento.

  * `Dockerfile`: Instruções para construir a imagem.
  * `src/`: Contém o script Python do cliente.
      * `cliente_monitoramento.py`: Conecta-se aos simuladores via OPC-UA para coletar os dados.
  * `requirements.txt`: Lista as bibliotecas necessárias, incluindo `asyncua` e a biblioteca do banco de dados (`psycopg2` para PostgreSQL).

#### Pasta `banco_de_dados/`

Esta pasta representa o serviço de banco de dados.

  * `.env`: Arquivo para variáveis de ambiente, utilizado para gerenciar credenciais do banco de dados de forma segura.

-----

### Lógica de Simulação

O arquivo `simulador_cnc.py` é o coração da simulação. Ele é composto por duas classes principais:

#### Classe `SimuladorCNC`

Esta classe modela a máquina CNC, mantendo seu estado e gerando dados.

```python
# simulador_cnc.py
import asyncio
import time
import random
from asyncua import Server, ua
from operador_cnc import OperadorCNC

class SimuladorCNC:
    def __init__(self, machine_id):
        self.machine_id = machine_id
        self.status = "IDLE"
        self.producao_total = 0
        self.posicao_eixos = {'x': 0.0, 'y': 0.0, 'z': 0.0}
        self.velocidade_fuso = 0.0
        self.alarmes_ativos = []

    def iniciar_ciclo(self):
        if self.status == "IDLE":
            self.status = "RUNNING"
            print(f"[{self.machine_id}] - Ciclo de produção iniciado.")

    def parar_ciclo(self):
        if self.status == "RUNNING":
            self.status = "IDLE"
            print(f"[{self.machine_id}] - Ciclo de produção parado.")

    def gerar_alarme(self, codigo_alarme="E100"):
        if codigo_alarme not in self.alarmes_ativos:
            self.alarmes_ativos.append(codigo_alarme)
            self.status = "ALARM"
            print(f"[{self.machine_id}] - ALARME ATIVO: {codigo_alarme}")

    def atualizar_estado(self):
        if self.status == "RUNNING":
            self.posicao_eixos['x'] += random.uniform(-0.5, 0.5)
            self.posicao_eixos['y'] += random.uniform(-0.5, 0.5)
            self.posicao_eixos['z'] += random.uniform(-0.5, 0.5)
            self.velocidade_fuso = 500.0
            
            if random.random() < 0.005:
                self.producao_total += 1
                print(f"[{self.machine_id}] - Peça #{self.producao_total} concluída.")

async def main(machine_id, endpoint_url):
    maquina_simulada = SimuladorCNC(machine_id)
    operador_simulado = OperadorCNC(maquina_simulada)

    server = Server()
    await server.init()
    server.set_endpoint(endpoint_url)
    
    uri = f"http://example.org/{machine_id}"
    idx = await server.register_namespace(uri)

    maquina_node = await server.nodes.objects.add_object(idx, machine_id)

    var_status = await maquina_node.add_variable(idx, "Status", maquina_simulada.status)
    var_producao = await maquina_node.add_variable(idx, "ProducaoTotal", maquina_simulada.producao_total)
    var_x = await maquina_node.add_variable(idx, "PosicaoX", maquina_simulada.posicao_eixos['x'])
    var_y = await maquina_node.add_variable(idx, "PosicaoY", maquina_simulada.posicao_eixos['y'])
    var_z = await maquina_node.add_variable(idx, "PosicaoZ", maquina_simulada.posicao_eixos['z'])
    var_velocidade = await maquina_node.add_variable(idx, "VelocidadeFuso", maquina_simulada.velocidade_fuso)
    var_alarmes = await maquina_node.add_variable(idx, "AlarmesAtivos", str(maquina_simulada.alarmes_ativos))
    
    print(f"[{machine_id}] - Servidor OPC-UA iniciado em {endpoint_url}")
    async with server:
        while True:
            await var_status.set_value(maquina_simulada.status)
            await var_producao.set_value(maquina_simulada.producao_total)
            await var_x.set_value(maquina_simulada.posicao_eixos['x'])
            await var_y.set_value(maquina_simulada.posicao_eixos['y'])
            await var_z.set_value(maquina_simulada.posicao_eixos['z'])
            await var_velocidade.set_value(maquina_simulada.velocidade_fuso)
            await var_alarmes.set_value(str(maquina_simulada.alarmes_ativos))
            
            operador_simulado.executar_acoes()
            maquina_simulada.atualizar_estado()
            
            await asyncio.sleep(1)

if __name__ == "__main__":
    import sys
    machine_id = sys.argv[1]
    endpoint_url = sys.argv[2]
    asyncio.run(main(machine_id, endpoint_url))

```

#### Classe `OperadorCNC`

Esta classe simula a interação humana com a máquina, adicionando dinamismo à simulação.

```python
# operador_cnc.py
import time
import random

class OperadorCNC:
    def __init__(self, maquina_simulada):
        self.maquina = maquina_simulada
        self.proxima_acao_em = time.time() + random.randint(10, 30)

    def executar_acoes(self):
        if time.time() >= self.proxima_acao_em:
            acao = random.choice(["ligar", "desligar", "falha"])
            
            if acao == "ligar" and self.maquina.status == "IDLE":
                self.maquina.iniciar_ciclo()
            elif acao == "desligar" and self.maquina.status == "RUNNING":
                self.maquina.parar_ciclo()
            elif acao == "falha" and self.maquina.status == "RUNNING":
                self.maquina.gerar_alarme(random.choice(["E101", "E205", "F303"]))
            
            self.proxima_acao_em = time.time() + random.randint(10, 30)
```

-----

### Comunicação via OPC-UA

O OPC-UA é o protocolo de comunicação utilizado para a troca de dados entre os simuladores e o cliente de monitoramento.

#### Servidor OPC-UA

Cada simulador CNC executa um servidor OPC-UA para expor seus dados. A função `main` do `simulador_cnc.py` é responsável por:

  * Instanciar o servidor OPC-UA.
  * Criar um **espaço de endereçamento** (`address space`), que é uma estrutura hierárquica de nós.
  * Mapear os atributos da classe `SimuladorCNC` para as variáveis do servidor OPC-UA.
  * Manter um loop assíncrono para atualizar os valores das variáveis em tempo real.

<!-- end list -->

```python
# simulador_cnc.py (continuação)
# ... Código das classes SimuladorCNC e OperadorCNC ...

async def main(machine_id, endpoint_url):
    """
    Função principal que inicia o servidor OPC-UA e a simulação.
    """
    # 1. Instanciar a máquina e o operador
    maquina_simulada = SimuladorCNC(machine_id)
    operador_simulado = OperadorCNC(maquina_simulada)

    # 2. Configurar o servidor OPC-UA
    server = Server()
    await server.init()
    server.set_endpoint(endpoint_url)
    
    # OPC-UA tem uma estrutura hierárquica. Criamos um "espaço de endereçamento".
    uri = f"http://example.org/{machine_id}"
    idx = await server.register_namespace(uri)

    # 3. Criar a estrutura de variáveis no servidor OPC-UA
    # "Objects" representam algo, como nossa máquina.
    maquina_node = await server.nodes.objects.add_object(idx, maquina_id)

    # "Variables" guardam os dados.
    var_status = await maquina_node.add_variable(idx, "Status", maquina_simulada.status)
    var_producao = await maquina_node.add_variable(idx, "ProducaoTotal", maquina_simulada.producao_total)
    var_x = await maquina_node.add_variable(idx, "PosicaoX", maquina_simulada.posicao_eixos['x'])
    var_y = await maquina_node.add_variable(idx, "PosicaoY", maquina_simulada.posicao_eixos['y'])
    var_z = await maquina_node.add_variable(idx, "PosicaoZ", maquina_simulada.posicao_eixos['z'])
    var_velocidade = await maquina_node.add_variable(idx, "VelocidadeFuso", maquina_simulada.velocidade_fuso)
    var_alarmes = await maquina_node.add_variable(idx, "AlarmesAtivos", str(maquina_simulada.alarmes_ativos))
    
    # 4. Iniciar o servidor
    print(f"[{machine_id}] - Servidor OPC-UA iniciado em {endpoint_url}")
    async with server:
        # 5. O loop principal que atualiza as variáveis
        while True:
            # Sincroniza o estado da simulação com as variáveis do servidor
            await var_status.set_value(maquina_simulada.status)
            await var_producao.set_value(maquina_simulada.producao_total)
            await var_x.set_value(maquina_simulada.posicao_eixos['x'])
            await var_y.set_value(maquina_simulada.posicao_eixos['y'])
            await var_z.set_value(maquina_simulada.posicao_eixos['z'])
            await var_velocidade.set_value(maquina_simulada.velocidade_fuso)
            await var_alarmes.set_value(str(maquina_simulada.alarmes_ativos))
            
            # Executa a lógica do operador e da máquina
            operador_simulado.executar_acoes()
            maquina_simulada.atualizar_estado()
            
            await asyncio.sleep(1) # Espera 1 segundo para o próximo ciclo

# Para rodar o script diretamente:
# if __name__ == "__main__":
#     import asyncio
#     # Exemplo de uso: asyncio.run(main("CNC_001", "opc.tcp://localhost:4840/freeopcua/server/"))
#     # O endpoint e o ID da máquina serão passados via linha de comando pelo Docker
```

#### Cliente OPC-UA

O script `cliente_monitoramento.py` atua como o cliente OPC-UA, conectando-se aos servidores e coletando os dados.

```python
# cliente_monitoramento.py
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
            # Note que a URI deve ser a mesma que você definiu no simulador
            uri = f"http://example.org/CNC_{endpoint_url.split(':')[-1]}" # Exemplo de como gerar a URI
            idx = await client.get_namespace_index(uri)

            # Encontrar os nós das variáveis
            maquina_node = await client.nodes.objects.get_child([f"{idx}:CNC_001"]) # Precisa ser dinâmico!
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
                'maquina_id': endpoint_url,
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
        print("-" * 20)
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
    # A lista de endpoints virá do script "starter-project.py"
    # Exemplo: ["opc.tcp://cnc1:4840/freeopcua/server/", "opc.tcp://cnc2:4840/freeopcua/server/"]
    endpoints = sys.argv[1:] 
    if not endpoints:
        print("Por favor, forneça os endpoints dos servidores como argumentos.")
    else:
        asyncio.run(main_monitoramento(endpoints))
```

-----

### Como Executar o Projeto

1.  **Pré-requisitos**: Certifique-se de ter o [Docker](https://www.docker.com/) instalado e em execução.
2.  **Executar o script**: Abra o terminal na pasta raiz do projeto e execute o seguinte comando:
    ```bash
    python starter-project.py
    ```
3.  **Configuração**: O script irá perguntar quantos simuladores de CNC você deseja criar. Insira um número e pressione `Enter`.
4.  **Início**: O script irá gerar o `docker-compose.yml` e iniciar todos os contêineres. A primeira execução pode levar alguns minutos, pois as imagens precisam ser construídas.
5.  **Verificar o Status**: Após a inicialização, você pode verificar o status dos contêineres com o comando:
    ```bash
    docker-compose ps
    ```
6.  **Visualizar os Logs**: Para ver a saída dos contêineres em tempo real, use o comando:
    ```bash
    docker-compose logs -f
    ```

Este projeto oferece uma base sólida para a construção de soluções de monitoramento e automação industrial, servindo como uma excelente ferramenta de aprendizado e desenvolvimento.