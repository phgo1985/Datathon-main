# Usa uma imagem base com Python
FROM python:3.11

# Define o diretório de trabalho
WORKDIR /app

# Copia apenas o requirements primeiro para aproveitar cache
COPY requirements.txt .

# Atualiza pip e instala dependências
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt
    
# Agora copia o restante do código
COPY . .

# Expõe a porta padrão do Flask
EXPOSE 5000

# Comando para rodar o app
CMD ["python", "app.py"]