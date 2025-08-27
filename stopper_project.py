# stopper_project.py
import subprocess
import os
import sys

def main():
    """
    Função principal que derruba o ambiente Docker.
    """
    print("Iniciando a limpeza do ambiente Docker...")
    try:
        # Para e remove os contêineres e a rede
        subprocess.run(["docker-compose", "down"], check=True)
        print("\nAmbiente Docker parado e removido com sucesso!")
        
        # Opcional: limpa as imagens que não estão mais sendo usadas
        # Esta linha não é estritamente necessária, mas é uma boa prática
        # subprocess.run(["docker", "image", "prune", "-f"], check=True)
        # print("Imagens Docker não usadas foram limpas.")
        
    except FileNotFoundError:
        print("Erro: Docker ou Docker Compose não encontrado. Verifique a instalação.")
        sys.exit(1)
    except subprocess.CalledProcessError as e:
        print(f"Ocorreu um erro ao executar o Docker Compose: {e}")
        print("Verifique se o Docker está em execução.")
        sys.exit(1)
        
if __name__ == "__main__":
    main()