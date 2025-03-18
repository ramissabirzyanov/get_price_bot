import logging
import re
import requests
import os
from lxml import html
from typing import Optional

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
from selenium.webdriver.remote.webdriver import WebDriver
# from selenium.webdriver.chrome.service import Service
# from webdriver_manager.chrome import ChromeDriverManager


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger()


def clean_price(price: str) -> Optional[float]:
    """Очищает цену от валютных символов, пробелов, запятых."""
    try:
        return float(re.sub(r"[^\d.]", "", price.replace(" ", "")))
    except ValueError:
        logger.error(f"Something wrong with price: {price}")
        return None


def get_selenium_driver() -> WebDriver:
    """Подключаемся к контейнеру Selenium через WebDriver."""

    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--disable-dev-shm-usage")

    # для запуска в контейнере:
    selenium_url = os.getenv("SELENIUM_URL")

    if not selenium_url:
        raise ValueError(
            "SELENIUM_URL не задан. Для работы в контейнере укажите URL Selenium Hub.\n"
            "Пример: http://selenium:4444/wd/hub"
        )
    driver = webdriver.Remote(
        command_executor=selenium_url,
        options=options
    )
    # для локальной разработки используется driver:
    # driver = webdriver.Chrome(
    #     service=Service(ChromeDriverManager().install()),
    #     options=options
    # )
    return driver


def fetch_price_selenium(url: str, xpath: str) -> Optional[float]:
    """Забирает цену с динамических сайтов с помощью Selenium"""
    try:
        driver = get_selenium_driver()
        driver.get(url)
        logger.info("🕒 loading the element...")
        price_element = WebDriverWait(driver, 10).until(
            ec.presence_of_element_located((By.XPATH, xpath))
        )
        price_text = price_element.text.strip()

        if not price_text:
            logger.warning("The element is hided probably or none. Getting text by JS...")
            price_text = driver.execute_script(
                "return arguments[0].textContent;",
                price_element
            ).strip()
            return clean_price(price_text)
        return clean_price(price_text)
    
    except (TimeoutException, NoSuchElementException, WebDriverException) as e:
        logger.error(f"Selenium ошибка: {str(e)}")
        return None

    finally:
        driver.quit()


def fetch_price_static(url: str, xpath: str) -> Optional[float]:
    """Забирает цену с статических сайтов с использованием requests и lxml"""
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        page_content = response.text
        tree = html.fromstring(page_content)
        prices = tree.xpath(xpath)
        if prices:
            price = prices[0].text_content().strip()
            return clean_price(price)
        return None

    except requests.RequestException as e:
        logger.error(f"HTTP request error: {e}")
        return None

    except Exception as e:
        logger.critical(f"Some mysterious error happened: {str(e)}")
        return None


def get_price(url: str, xpath: str) -> Optional[float]:
    """
    Получает цену товара.
    Какой парсер будет использоваться зависит от сайта
    """
    price = fetch_price_static(url, xpath)

    if price is not None:
        return price

    logger.info("Trying Selenium...")
    price = fetch_price_selenium(url, xpath)
    return price
