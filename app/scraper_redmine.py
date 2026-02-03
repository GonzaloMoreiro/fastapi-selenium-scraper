import os
import time
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options

from app.config import DOWNLOAD_PATH, CHROME_BIN, CHROMEDRIVER_PATH

logger = logging.getLogger(__name__)


def excel_download():
    os.makedirs(DOWNLOAD_PATH, exist_ok=True)

    chrome_options = Options()
    chrome_options.binary_location = CHROME_BIN
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')

    driver = webdriver.Chrome(service=Service(CHROMEDRIVER_PATH), options=chrome_options)

    try:
        driver.get("https://redmine.voxia.es/issues/4032")
        time.sleep(40)
    finally:
        driver.quit()
