import os

RUTA_ARCHIVO = os.getenv("RUTA_ARCHIVO", "/app/downloads/mentions.csv")
RUTA_DESCARGA = os.getenv("RUTA_DESCARGA", "downloads/data_procesada.txt")

N8N_WEBHOOK_URL = os.getenv("N8N_WEBHOOK_URL", "http://localhost:5678/webhook-test")

DOWNLOAD_PATH = os.getenv("PYTHON_DOWNLOAD_PATH", "/app/downloads")
CHROME_BIN = os.getenv("CHROME_BIN", "/usr/bin/google-chrome")
CHROMEDRIVER_PATH = os.getenv("CHROMEDRIVER_PATH", "/usr/local/bin/chromedriver")
