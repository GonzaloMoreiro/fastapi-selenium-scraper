FROM python:3.10-slim

# Dependencias del sistema para Chrome
RUN apt-get update && apt-get install -y \
    wget \
    unzip \
    curl \
    gnupg \
    ca-certificates \
    fonts-liberation \
    libnss3 \
    libatk-bridge2.0-0 \
    libxkbcommon0 \
    libgtk-3-0 \
    libxdamage1 \
    libxrandr2 \
    libasound2 \
    libgbm1 \
    libxshmfence1 \
    libu2f-udev \
    chromium \
    chromium-driver \
    && rm -rf /var/lib/apt/lists/*

ENV CHROME_BIN=/usr/bin/chromium
ENV CHROMEDRIVER_PATH=/usr/bin/chromedriver

WORKDIR /app

COPY python/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app
COPY python/app.py .

EXPOSE 8000

CMD ["python", "app.py"]
