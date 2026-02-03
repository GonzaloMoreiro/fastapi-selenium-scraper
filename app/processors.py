from app.scraper_brandwatch import web_scraping
from app.file_utils import renombrar_archivo, process_data
from app.integrations import send_data_to_n8n


def run_mentions(url):
    web_scraping(url)
    archivo = renombrar_archivo("/app/downloads", "mentions")
    df = process_data("/app/downloads", "mentions")
    return send_data_to_n8n(df.to_dict())