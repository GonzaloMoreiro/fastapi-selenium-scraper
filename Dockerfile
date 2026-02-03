FROM python:3.11-slim

# Instalar dependencias del sistema y Chromium completo
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    unzip \
    curl \
    chromium \
    chromium-driver \
    libnss3 \
    libatk1.0-0 \
    libx11-6 \
    libxcomposite1 \
    libxrandr2 \
    libxdamage1 \
    libxfixes3 \
    libxi6 \
    libgtk-3-0 \
    libcups2 \
    libdrm2 \
    libgbm1 \
    && rm -rf /var/lib/apt/lists/*

# Variables de entorno para Selenium
ENV CHROME_BIN=/usr/bin/chromium
ENV CHROMEDRIVER_PATH=/usr/bin/chromedriver

# Directorio de trabajo
WORKDIR /app

# Copiar requirements y código
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

# Carpeta de descargas
RUN mkdir -p /app/downloads

EXPOSE 8000

CMD ["uvicorn", "app.app:app", "--host", "0.0.0.0", "--port", "8000"]