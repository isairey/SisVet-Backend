# Dockerfile para Sistema de Gestión Veterinaria Backend
# Multi-stage build para optimizar el tamaño de la imagen

# Stage 1: Builder - Instalar dependencias y preparar el entorno
FROM python:3.11-slim as builder

# Variables de entorno para Python
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Instalar dependencias del sistema necesarias para compilar paquetes Python
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Crear directorio de trabajo
WORKDIR /app

# Copiar requirements y instalar dependencias
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Stage 2: Runtime - Imagen final optimizada
FROM python:3.11-slim

# Variables de entorno
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/home/appuser/.local/bin:$PATH"

# Instalar solo runtime dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    libpq5 \
    && rm -rf /var/lib/apt/lists/* \
    && useradd -m -u 1000 appuser

# Crear directorio de trabajo
WORKDIR /app

# Copiar dependencias instaladas desde el builder
COPY --from=builder /root/.local /home/appuser/.local

# Script de entrada (copiar antes de cambiar usuario para poder hacer chmod)
COPY docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh

# Copiar código de la aplicación
COPY --chown=appuser:appuser . .

# Cambiar al usuario no-root
USER appuser

# Exponer el puerto
EXPOSE 8000

# Comando por defecto
ENTRYPOINT ["/docker-entrypoint.sh"]
CMD ["gunicorn", "clinica_veterinaria.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3", "--timeout", "120", "--access-logfile", "-", "--error-logfile", "-"]

