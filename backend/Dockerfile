# Etapa 1: Build
FROM python:3.12-slim AS builder

# Instalar dependências do sistema necessárias
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    libpq-dev \
    libjpeg-dev \
    zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

# Configurações do Poetry
ENV POETRY_VERSION=1.6.1
ENV POETRY_HOME="/opt/poetry"
ENV PATH="$POETRY_HOME/bin:$PATH"
ENV POETRY_VIRTUALENVS_CREATE=false

# Instalar o Poetry
RUN curl -sSL https://install.python-poetry.org | python -

# Definir diretório de trabalho
WORKDIR /app

# Copiar arquivos de dependências
COPY pyproject.toml poetry.lock ./

# Instalar dependências
RUN poetry install --no-root --no-dev

# Exportar as dependências para requirements.txt
RUN poetry export -f requirements.txt --without-hashes -o requirements.txt

# Copiar o código da aplicação
COPY . .

# Etapa 2: Imagem Final
FROM python:3.12-slim

# Instalar dependências do sistema necessárias em tempo de execução
RUN apt-get update && apt-get install -y --no-install-recommends \
    libjpeg-dev \
    zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

# Definir diretório de trabalho
WORKDIR /app

# Copiar o requirements.txt da etapa de build
COPY --from=builder /app/requirements.txt ./

# Instalar dependências usando pip
RUN pip install --no-cache-dir -r requirements.txt

# Copiar o código da aplicação da etapa de build
COPY --from=builder /app .

# Expor a porta
EXPOSE 5000

# Definir variáveis de ambiente
ENV SUPABASE_URL='https://pvohcqzdzmzvzidyvjss.supabase.co'
ENV SUPABASE_KEY='eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InB2b2hjcXpkem16dnppZHl2anNzIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MjcxMTUyNTAsImV4cCI6MjA0MjY5MTI1MH0.sopZMZLs8Kl8miYsS9rKhQ7sn38eRHQDIKfu2ltl1Yg'
ENV BUCKET_NAME='generate'

# Comando para iniciar a aplicação
CMD ["python", "app.py"]
