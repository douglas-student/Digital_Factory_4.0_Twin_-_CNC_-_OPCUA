# Usa uma imagem oficial do PHP com Apache
FROM php:8.1-apache

# Define o diretório de trabalho do servidor web
WORKDIR /var/www/html/

# Instala as dependências do sistema para o PostgreSQL
RUN apt-get update && apt-get install -y \
    libpq-dev \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Habilita o mod_rewrite do Apache para URLs amigáveis
RUN a2enmod rewrite

# Instala as extensões PHP necessárias para o PostgreSQL
RUN docker-php-ext-install pdo pdo_pgsql

# Copia os arquivos de código-fonte da aplicação para o contêiner
COPY src/ /var/www/html/

# Copia o arquivo de configuração php.ini
COPY php.ini /usr/local/etc/php/conf.d/

# Expondo a porta padrão do Apache
EXPOSE 80