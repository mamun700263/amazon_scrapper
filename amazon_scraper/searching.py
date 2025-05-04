import time
from urllib.parse import quote_plus
from bs4 import BeautifulSoup
from utils.common import scroll_and_wait, sleeper , save_as
from utils.selenium_utils import ScraperConfig

from logger import logger


class AmazonScraper:
    def __init__(self, config: ScraperConfig):
        self.config = config
        self.driver = config.driver
        self.url = "https://www.amazon.com"
        logger.info("🚀 AmazonScraper initialized")

    def get_search_url(self, keyword: str) -> str:
        encoded = quote_plus(keyword)
        search_url = f"{self.url}/s?k={encoded}"
        logger.debug(f"🔗 Generated search URL: {search_url}")
        return search_url

    def scrape_search_results(self, keyword: str, wait_time=3) -> str:
        url = self.get_search_url(keyword)
        logger.info(f"🌐 Navigating to search page: {url}")
        try:
            self.driver.get(url)
            scroll_and_wait(self.driver)
            time.sleep(wait_time)
            logger.info("✅ Page loaded and ready for scraping")
            return self.driver.page_source
        except Exception as e:
            logger.error(f"❌ Error loading page for keyword '{keyword}': {e}")
            return ""

    def pagination(self, soup):
        logger.debug("📄 Checking for pagination...")
        try:
            next_page = soup.find('a', class_='s-pagination-next')    
            if not next_page or not next_page.get("href"):
                logger.warning("⚠️ No next page link found")
                return None
            next_url = f'{self.url}{next_page["href"]}'
            logger.info(f"➡️ Found next page URL: {next_url}")
            return next_url
        except Exception as e:
            logger.error(f"❌ Pagination error: {e}")
            return None

    def quit(self):
        logger.info("🛑 Quitting WebDriver")
        self.driver.quit()

def soup_maker(response):
    try:
        soup = BeautifulSoup(response, 'lxml')
        logger.info("✅ Soup created successfully")
        return soup
    except Exception as e:
        logger.error(f"❌ Failed to create soup: {e}")
        return None

def list_items(soup):
    try:
        logger.info("🔍 Locating product list items...")
        items = soup.select('div[role="listitem"]')
        if not items:
            logger.warning("⚠️ No product list items found")
            return []
        logger.info(f"✅ Found {len(items)} product items")
        return items
    except Exception as e:
        logger.error(f"❌ Error locating list items: {e}")
        return []

def extract_text(item, selector, attr=None):
    try:
        el = item.find(selector)
        if not el:
            return ""
        return el.get(attr) if attr else el.text.strip()
    except Exception as e:
        logger.warning(f"⚠️ Extraction failed for {selector}: {e}")
        return ""

def title_extractor(item):
    title = extract_text(item, 'h2')
    if title:
        logger.debug(f"📝 Title: {title}")
    return title

def image_extractor(item):
    return extract_text(item, 'img', 'src')

def link_extractor(item, base_url):
    link = extract_text(item, 'a', 'href')
    return f"{base_url}{link}" if link else ""

def extractor(soup, base_url):
    if not soup:
        logger.error("❌ No soup provided to extractor")
        return []

    items = list_items(soup)
    results = []

    for item in items:
        title = title_extractor(item)
        if not title:
            continue  # skip items with no title

        product = {
            'Title': title,
            'Image': image_extractor(item),
            'Link': link_extractor(item, base_url)
        }
        results.append(product)

    logger.info(f"✅ Extracted {len(results)} products successfully")
    return results



def main():
    config = ScraperConfig()
    amazon = AmazonScraper(config=config)

    try:
        results = amazon.scrape_all_pages('headphone', max_pages=2)
        save_as(results, 'first.csv')
    finally:
        amazon.quit()

if __name__ == "__main__":
    main()