# scraper.py

import re
import time

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException

BASE_URL = "https://www.city24.lv"
SEARCH_URL = "https://www.city24.lv/real-estate-search/commercials-for-sale"


def get_text(card, css):
    el = card.select_one(css)
    return el.get_text(strip=True) if el else ""


def clean_price(text):
    digits = re.sub(r"[^\d]", "", text)
    return int(digits) if digits else None


def is_skeleton(text):
    core = text.replace(" ", "").lower()
    return not core or all(ch == "m" for ch in core)


def listings_loaded(driver):
    real = 0
    for c in driver.find_elements(By.CSS_SELECTOR, "div.object--result"):
        try:
            addr = c.find_element(By.CSS_SELECTOR, ".object__address").get_attribute("textContent") or ""
        except Exception:
            addr = ""
        if not is_skeleton(addr):
            real += 1
    return real >= 20


def parse_listings(html):
    """Extract a list of listing dicts from a page's HTML."""
    soup = BeautifulSoup(html, "html.parser")
    listings = []
    for card in soup.select("div.object--result"):
        address = get_text(card, ".object__address")
        if is_skeleton(address):
            continue
        price_text = get_text(card, ".object-price__main-price")
        link_el = card.select_one("a.object__attributes")
        link = BASE_URL + link_el["href"] if link_el and link_el.has_attr("href") else ""
        listings.append({
            "address": address,
            "city": get_text(card, ".object__area"),
            "category": get_text(card, ".object__purpose"),
            "price_text": price_text,
            "price_eur": clean_price(price_text),
            "features": get_text(card, ".object__main-features"),
            "link": link,
        })
    return listings


def scrape_city24(max_pages=3):
    """Scrape commercial listings from city24.lv across up to max_pages pages."""
    options = Options()
    driver = webdriver.Chrome(options=options)
    listings = []
    try:
        for page in range(1, max_pages + 1):
            url = SEARCH_URL if page == 1 else f"{SEARCH_URL}/pg={page}"
            driver.get(url)
            try:
                WebDriverWait(driver, 30).until(listings_loaded)
            except TimeoutException:
                pass  # last page may have fewer than 20 listings
            page_listings = parse_listings(driver.page_source)
            if not page_listings:
                break
            listings.extend(page_listings)
            time.sleep(1)  # courtesy delay between pages
    finally:
        driver.quit()
    return listings