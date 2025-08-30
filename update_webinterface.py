# update_web.py
import subprocess
import os
import sys

def main():
    """
    Copia os arquivos da plataforma web para o contêiner em execução.
    """
    container_name = "web_dashboard"

    print(f"Atualizando arquivos no contêiner '{container_name}'...")

    try:
        # Copia o index.php
        subprocess.run(["docker", "cp", "php_web/src/index.php", f"{container_name}:/var/www/html/index.php"], check=True)
        # Copia o db_connection.php
        subprocess.run(["docker", "cp", "php_web/src/includes/db_connection.php", f"{container_name}:/var/www/html/includes/db_connection.php"], check=True)
        # Copia o style.css
        subprocess.run(["docker", "cp", "php_web/src/assets/css/style.css", f"{container_name}:/var/www/html/assets/css/style.css"], check=True)
        
        print("\nArquivos atualizados com sucesso!")
        print("Agora você pode recarregar a página no seu navegador para ver as mudanças.")

    except FileNotFoundError:
        print("Erro: Verifique se o Docker está instalado e se o contêiner 'web_dashboard' está em execução.")
        sys.exit(1)
    except subprocess.CalledProcessError as e:
        print(f"Ocorreu um erro ao copiar os arquivos: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()