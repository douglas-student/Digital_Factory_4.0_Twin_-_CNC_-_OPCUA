# starter_project.py
import subprocess
import os
import sys

def listar_ips_containers(servicos):
    """
    Lista os endereços IP dos contêineres após o início.
    """
    print("\nVerificando endereços IP dos contêineres...")
    for servico in servicos:
        try:
            container_ip = subprocess.check_output(
                ["docker", "inspect", "-f", '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}', servico],
                text=True
            ).strip()
            print(f"Serviço '{servico}': IP {container_ip if container_ip else 'Não encontrado'}")
        except subprocess.CalledProcessError:
            print(f"Erro ao inspecionar o serviço '{servico}'. Pode não estar rodando.")

def gerar_docker_compose(num_simuladores):
    """
    Gera o conteúdo do arquivo docker-compose.yml dinamicamente.
    """
    yml_content = """
networks:
  industria40_net:
    driver: bridge

services:
  banco_de_dados:
    image: postgres:13
    container_name: postgres_db
    networks:
      - industria40_net
    environment:
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=password
      - POSTGRES_DB=fabrica
    volumes:
      - ./banco_de_dados_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U user -d fabrica"]
      interval: 10s
      timeout: 5s
      retries: 5

  monitoramento:
    build: ./monitoramento
    container_name: cliente_monitoramento
    networks:
      - industria40_net
    environment:
      - POSTGRES_HOST=banco_de_dados
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=password
      - POSTGRES_DB=fabrica
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
    environment:
      - POSTGRES_HOST=banco_de_dados
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=password
      - POSTGRES_DB=fabrica
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
    servicos_para_verificar = ["postgres_db", "web_dashboard", "cliente_monitoramento"] + [f"cnc_simulador_{i}" for i in range(1, num_simuladores + 1)]
    try:
        subprocess.run(["docker-compose", "up", "--build", "-d"], check=True)
        print("\nTodos os contêineres foram iniciados com sucesso!")
        
        listar_ips_containers(servicos_para_verificar)
        
        print("\nPara acessar a plataforma web, abra seu navegador em http://localhost:8080")
    except subprocess.CalledProcessError as e:
        print(f"\nOcorreu um erro ao executar o Docker Compose: {e}")
        print("Verifique se o Docker está instalado e em execução.")

if __name__ == "__main__":
    main()