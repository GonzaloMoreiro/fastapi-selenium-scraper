import requests
from app.config import N8N_WEBHOOK_URL


def send_data_to_n8n(payload):
    response = requests.post(N8N_WEBHOOK_URL, json=payload)
    response.raise_for_status()
    return response.text