from utils.common import *
from utils.amazon import *
from utils.selenium_utils import *

from log_config import get_logger
logger = get_logger('Searcing')


def main():
    config = ScraperConfig()
    amazon = AmazonScraper(config)
    driver = amazon.driver
    results = amazon.scrape_all_pages("keyboard ", max_pages=5)
    save_as(items=results, file_name="keyboard.json")
    amazon.quit()

if __name__==__main__:
    main()
