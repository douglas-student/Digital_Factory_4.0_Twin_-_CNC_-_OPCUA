# update_webinterface.py
import subprocess
import os
import sys

def main():
    """
    Copia a pasta de código-fonte da plataforma web para o contêiner em execução.
    """
    container_name = "web_dashboard"
    source_dir_src = "php_web/src"
    destination_dir_html = "/var/www/html/"

    print(f"Atualizando arquivos no contêiner '{container_name}'...")

    try:
        # 1. Limpa o diretório de destino no contêiner antes de copiar
        print("Limpando a pasta do servidor web no contêiner...")
        subprocess.run(["docker", "exec", container_name, "rm", "-rf", f"{destination_dir_html}*"], check=True)

        # 2. Copia o conteúdo da pasta 'src' para o diretório raiz do servidor web
        for item in os.listdir(source_dir_src):
            full_path_source = os.path.join(source_dir_src, item)
            subprocess.run(["docker", "cp", full_path_source, f"{container_name}:{destination_dir_html}"], check=True)

        # 3. Copia o arquivo php.ini especificamente
        subprocess.run(["docker", "cp", "php_web/php.ini", f"{container_name}:/usr/local/etc/php/conf.d/"], check=True)
        
        print("Arquivos copiados com sucesso!")
        
        # 4. Reinicia o contêiner web para aplicar as mudanças
        print(f"Reiniciando o contêiner '{container_name}' para aplicar as mudanças...")
        subprocess.run(["docker", "restart", container_name], check=True)
        
        print("\nPronto! A interface web foi atualizada e o contêiner reiniciado.")
        print("Agora você pode recarregar a página no seu navegador para ver as mudanças.")

    except FileNotFoundError:
        print("Erro: Verifique se o Docker está instalado e se o contêiner 'web_dashboard' está em execução.")
        sys.exit(1)
    except subprocess.CalledProcessError as e:
        print(f"Ocorreu um erro ao executar comandos Docker: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()