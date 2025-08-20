# Base
FROM python:3.11-slim

# Variables de entorno en Python
ENV PYTHONDONTWRITEBYTECODE=1  \
    PYTHONUNBUFFERED=1 \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_NO_INTERACTION=1

# Crear usuario no root
RUN useradd -m -u 10001 appuser

# Directorio de trabajo
WORKDIR /app


# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    curl build-essential && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Instalar Poetry
RUN pip install --no-cache-dir poetry

# Copiar solo archivos de dependencias primero (para cachear)
COPY pyproject.toml poetry.lock* ./

# Instalar dependencias del proyecto
RUN poetry install --without dev --no-root

# Copiar resto del servicio
COPY . .

# Crear carpeta de logs con permisos correctos
RUN mkdir -p /app/logs && chown -R appuser:appuser /app/logs

# Cambiar a usuario no root
USER appuser

# Exponer el puerto del servicio DE CryptoMesh
EXPOSE 19000

# Comando para iniciar el servicio
CMD ["uvicorn", "cryptomesh.server:app", "--host", "0.0.0.0", "--port", "19000"]

