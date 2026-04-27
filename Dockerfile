FROM python:3.11-slim

# Define a pasta de trabalho dentro do Docker
WORKDIR /app

# Instala ferramentas do sistema necessárias
RUN apt-get update && apt-get install -y gcc curl && rm -rf /var/lib/apt/lists/*

# Copia e instala as dependências
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia todo o código do seu projeto para dentro do Docker
COPY . .

# Comando para rodar a sua API
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]