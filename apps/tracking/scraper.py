# apps/products/scraper.py
import requests
from bs4 import BeautifulSoup

def scrape_market_price(url, retailer_name):
    headers = {"User-Agent": "Mozilla/5.0 ..."}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    if "Amazon" in retailer_name:
        # كود تخيلي لجلب السعر بناءً على الـ HTML class بتاع أمازون
        price_text = soup.find("span", {"class": "a-price-whole"}).text
        return float(price_text.replace(',', '')), True
        
    elif "Noon" in retailer_name:
        price_text = soup.find("div", {"class": "priceNow"}).text
        return float(price_text), True
        
    return None, False