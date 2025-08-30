# tecnico_manutencao.py
import time
import random

class TecnicoManutencao:
    def __init__(self, maquina_simulada):
        self.maquina = maquina_simulada
        self.proxima_acao_em = time.time() + random.randint(30, 60) # Tenta consertar a cada 30-60s

    def executar_acoes(self):
        if time.time() >= self.proxima_acao_em:
            if self.maquina.status == "ALARM" or self.maquina.status == "WAITING_FOR_REPAIR":
                print(f"[{self.maquina.machine_id}] - Técnico de manutenção inspecionando a máquina...")
                
                # Se a máquina está aguardando peças, há uma chance de que elas cheguem
                if self.maquina.status == "WAITING_FOR_REPAIR":
                    if random.random() < 0.5: # 50% de chance de as peças chegarem
                        print(f"[{self.maquina.machine_id}] - Peças de reparo chegaram.")
                        self.maquina.status = "ALARM" # Agora o técnico pode tentar o reparo
                    else:
                        print(f"[{self.maquina.machine_id}] - Peças ainda não chegaram. Aguardando...")
                
                # Se a máquina está em estado de ALARM, o técnico tenta consertar
                if self.maquina.status == "ALARM":
                    if random.random() < 0.8: # 80% de chance de consertar
                        print(f"[{self.maquina.machine_id}] - Técnico conseguiu consertar o problema.")
                        self.maquina.limpar_alarme()
                    else: # 20% de chance de falha
                        print(f"[{self.maquina.machine_id}] - Técnico não conseguiu consertar. Máquina aguardando peças.")
                        self.maquina.status = "WAITING_FOR_REPAIR"

            self.proxima_acao_em = time.time() + random.randint(30, 60)