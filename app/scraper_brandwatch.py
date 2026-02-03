import os
import time
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import ElementClickInterceptedException

import os

MAIL_BRANDWATCH = os.getenv("MAIL_BRANDWATCH")
PASSWORD_BRANDWATCH = os.getenv("PASSWORD_BRANDWATCH")
from app.config import DOWNLOAD_PATH, CHROME_BIN, CHROMEDRIVER_PATH

logger = logging.getLogger(__name__)


def remove_intercom_iframe(driver):
    try:
        script = """
        var iframes = document.getElementsByTagName('iframe');
        for(var i = 0; i < iframes.length; i++) {
            if(iframes[i].outerHTML.toLowerCase().includes('intercom')) {
                iframes[i].remove();
            }
        }
        """
        driver.execute_script(script)
    except Exception:
        pass


def try_click_element(driver, element, max_attempts=3):
    for _ in range(max_attempts):
        try:
            element.click()
            return
        except ElementClickInterceptedException:
            remove_intercom_iframe(driver)
            ActionChains(driver).move_to_element(element).click().perform()


def web_scraping(url):
    os.makedirs(DOWNLOAD_PATH, exist_ok=True)

    chrome_options = Options()
    chrome_options.binary_location = CHROME_BIN
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_experimental_option("prefs", {
        "download.default_directory": DOWNLOAD_PATH,
        "download.prompt_for_download": False
    })

    service = Service(CHROMEDRIVER_PATH)
    driver = webdriver.Chrome(service=service, options=chrome_options)
    wait = WebDriverWait(driver, 30)

    try:
        driver.get(url)

        wait.until(EC.presence_of_element_located((By.NAME, "email"))).send_keys(mail_brandwatch)
        driver.find_element(By.NAME, "password").send_keys(contrasenia_brandwatch)
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

        cookie_button = wait.until(EC.element_to_be_clickable((By.ID, "onetrust-accept-btn-handler")))
        try_click_element(driver, cookie_button)

        export_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'button.export.db.grey.iconAsButton')))
        try_click_element(driver, export_button)

        csv_button = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "li[data-export-format='csv']")))
        try_click_element(driver, csv_button)

        time.sleep(20)

    finally:
        driver.quit()
