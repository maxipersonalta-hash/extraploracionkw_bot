# Usamos una imagen ligera de Python 3.11
FROM python:3.11-slim

# Evita que Python escriba archivos .pyc en disco y fuerza el log en tiempo real
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Creamos y establecemos el directorio de trabajo
WORKDIR /app

# Copiamos primero los requerimientos para aprovechar el caché de Docker
COPY requirements.txt .

# Instalamos las dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copiamos el resto del código (tu bot.py)
COPY . .

# Comando para ejecutar el bot
CMD ["python", "bot.py"]
