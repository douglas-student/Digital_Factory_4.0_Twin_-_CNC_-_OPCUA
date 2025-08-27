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