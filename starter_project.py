# starter_project.py
import subprocess
import os
import sys

def gerar_docker_compose(num_simuladores):
    """
    Gera o conteúdo do arquivo docker-compose.yml dinamicamente.
    """
    yml_content = """
version: '3.8'

networks:
  industria40_net:
    driver: bridge
    ipam:
      config:
        - subnet: 172.20.0.0/24
          gateway: 172.20.0.1

services:
  banco_de_dados:
    image: postgres:13
    container_name: postgres_db
    networks:
      industria40_net:
        ipv4_address: 172.20.0.2
    environment:
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=password
      - POSTGRES_DB=fabrica
    volumes:
      - ./banco_de_dados_data:/var/lib/postgresql/data

  monitoramento:
    build: ./monitoramento
    container_name: cliente_monitoramento
    networks:
      - industria40_net
    depends_on:
      - banco_de_dados
"""
    endpoints = " ".join([f"opc.tcp://cnc_simulador_{i}:4840/freeopcua/server/" for i in range(1, num_simuladores + 1)])
    
    yml_content += f"""\
    command: python /app/src/cliente_monitoramento.py {endpoints}
"""
    
    yml_content += """
  web:
    build: ./php_web
    container_name: web_dashboard
    ports:
      - "8080:80"
    networks:
      - industria40_net
    depends_on:
      - banco_de_dados
"""
    
    for i in range(1, num_simuladores + 1):
        yml_content += f"""
  cnc_simulador_{i}:
    build: ./simulador_cnc
    container_name: cnc_simulador_{i}
    networks:
      - industria40_net
    ports:
      - "484{i}:4840"
    command: python /app/src/simulador_cnc.py cnc_simulador_{i} opc.tcp://0.0.0.0:4840/freeopcua/server/
"""
    return yml_content

def main():
    """
    Ponto de entrada do script.
    """
    try:
        num_simuladores = int(input("Quantos simuladores de CNC você deseja criar? "))
        if num_simuladores < 1:
            print("Por favor, insira um número maior que zero.")
            sys.exit(1)
    except ValueError:
        print("Entrada inválida. Por favor, digite um número.")
        sys.exit(1)

    print("Gerando o arquivo docker-compose.yml...")
    with open("docker-compose.yml", "w") as f:
        f.write(gerar_docker_compose(num_simuladores))

    print("Iniciando os contêineres. Isso pode demorar na primeira vez...")
    try:
        subprocess.run(["docker-compose", "up", "--build", "-d"], check=True)
        print("\nTodos os contêineres foram iniciados com sucesso!")
        print("Verifique o status com 'docker-compose ps' ou os logs com 'docker-compose logs -f'.")
        print("\nPara acessar a plataforma web, abra seu navegador em http://localhost:8080")
    except subprocess.CalledProcessError as e:
        print(f"\nOcorreu um erro ao executar o Docker Compose: {e}")
        print("Verifique se o Docker está instalado e em execução.")

if __name__ == "__main__":
    main()