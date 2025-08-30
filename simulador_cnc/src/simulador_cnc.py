# simulador_cnc.py
import asyncio
import time
import random
from asyncua import Server, ua
from operador_cnc import OperadorCNC
from tecnico_manutencao import TecnicoManutencao

class SimuladorCNC:
    def __init__(self, machine_id):
        self.machine_id = machine_id
        self.status = "IDLE" # IDLE, RUNNING, ALARM, WAITING_FOR_REPAIR
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

    def limpar_alarme(self):
        if self.status == "ALARM":
            self.alarmes_ativos = []
            self.status = "IDLE"
            print(f"[{self.machine_id}] - Alarme limpo. Status retornado para IDLE.")

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
    tecnico_simulado = TecnicoManutencao(maquina_simulada)

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
            tecnico_simulado.executar_acoes()
            maquina_simulada.atualizar_estado()
            
            await asyncio.sleep(1)

if __name__ == "__main__":
    import sys
    machine_id = sys.argv[1]
    endpoint_url = sys.argv[2]
    asyncio.run(main(machine_id, endpoint_url))