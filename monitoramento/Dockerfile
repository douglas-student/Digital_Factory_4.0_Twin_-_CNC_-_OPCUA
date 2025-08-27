# Usa uma imagem oficial do Python como base
FROM python:3.9-slim

# Define o diretório de trabalho dentro do contêiner
WORKDIR /app

# Copia o arquivo de requisitos para o contêiner
COPY requirements.txt .

# Instala as dependências do Python
RUN pip install -r requirements.txt

# Copia o código-fonte da aplicação para o contêiner
COPY src/ /app/src/

# O comando para iniciar a aplicação é definido no docker-compose.yml
# CMD será sobrescrito pelo comando especificado no docker-compose.yml