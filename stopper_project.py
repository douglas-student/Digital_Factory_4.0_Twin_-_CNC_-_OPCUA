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
        # Para e remove os contêineres e redes, mas mantém os volumes
        subprocess.run(["docker-compose", "down", "--remove-orphans"], check=True)
        print("\nAmbiente Docker parado e removido com sucesso!")
        
        # Pergunta ao usuário se deseja apagar o volume de dados
        resposta = input("Deseja apagar o volume de dados do banco de dados? (s/n): ")
        if resposta.lower() == 's':
            print("Apagando o volume de dados...")
            
            if os.name == 'nt': # Verifica se o sistema operacional é Windows
                subprocess.run(["rmdir", "/s", "/q", "banco_de_dados_data"], check=True, shell=True)
            else: # Considera sistemas Unix-like (Linux, macOS)
                subprocess.run(["sudo", "rm", "-rf", "banco_de_dados_data"], check=True)

            print("Volume de dados removido com sucesso!")
        
    except FileNotFoundError:
        print("Erro: Docker ou Docker Compose não encontrado. Verifique a instalação.")
        sys.exit(1)
    except subprocess.CalledProcessError as e:
        print(f"Ocorreu um erro ao executar o Docker Compose: {e}")
        print("Verifique se o Docker está em execução.")
        sys.exit(1)
        
if __name__ == "__main__":
    main()