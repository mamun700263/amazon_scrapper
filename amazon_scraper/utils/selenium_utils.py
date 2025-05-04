import csv
import json
import random
import time
from urllib.parse import quote_plus

import lxml
import pandas as pd
import requests
import undetected_chromedriver as uc
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
# from selenium import webdriver
from seleniumwire import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service as ChromeService
from logger import logger

from .common import scroll_and_wait, sleeper


SCRAPEOPS_API_KEY = '576b5061-9bb7-4b03-a00f-4308452d920a' 

class ScraperConfig:
    def __init__(
        self,
        use_uc=False,
        headless=False,
        incognito=True,
        user_agent=None,
        use_scrapeops=False,
        use_seleniumwire=False,
    ):
        self.use_uc = use_uc
        self.headless = headless
        self.incognito = incognito
        self.use_scrapeops = use_scrapeops
        self.use_seleniumwire = use_seleniumwire

        # Setup proxy if enabled
        if self.use_scrapeops:
            self.proxy = f"http://scrapeops.headless_browser_mode=true:{SCRAPEOPS_API_KEY}@proxy.scrapeops.io:5353"
        else:
            self.proxy = None

        self.user_agents = [
            # (Add more if you want to expand it later)
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Linux; Android 14; SM-S918B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Mobile Safari/537.36",
            "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/537.36 (KHTML, like Gecko) Version/17.0 Mobile Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/122.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Firefox/120.0 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64; rv:120.0) Gecko/20100101 Firefox/120.0",
            "Mozilla/5.0 (Linux; Android 14; SM-S918B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Mobile Safari/537.36",
            "Mozilla/5.0 (Linux; Android 13; Pixel 7 Pro) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Mobile Safari/537.36",
            "Mozilla/5.0 (Linux; Android 12; SM-G991B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
            "Mozilla/5.0 (Android 13; Mobile; rv:120.0) Gecko/120.0 Firefox/120.0",
            "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/537.36 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/537.36",
            "Mozilla/5.0 (iPhone; CPU iPhone OS 16_5 like Mac OS X) AppleWebKit/537.36 (KHTML, like Gecko) CriOS/120.0.0.0 Mobile/15E148 Safari/537.36",
            "Mozilla/5.0 (iPad; CPU OS 16_1 like Mac OS X) AppleWebKit/537.36 (KHTML, like Gecko) Version/16.1 Mobile/15E148 Safari/537.36",
        ]

        self.random_user_agent = user_agent or random.choice(self.user_agents)
        self.driver = self._init_driver()

    def _init_driver(self):
        if self.use_uc:
            logger.info("⚙️ Using undetected_chromedriver (UC)")
            return self._get_uc_driver()
        else:
            logger.info("⚙️ Using standard Chrome driver")
            return self._get_normal_driver()

    def _get_uc_driver(self):
        options = uc.ChromeOptions()

        if self.headless:
            options.add_argument("--headless=new")
        if self.incognito:
            options.add_argument("--incognito")
        if self.proxy:
            options.add_argument(f"--proxy-server={self.proxy}")

        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--disable-popup-blocking")
        options.add_argument("--disable-infobars")
        options.add_argument("--start-maximized")
        options.add_argument("--window-size=1920,1080")
        options.add_argument(f"user-agent={self.random_user_agent}")

        return uc.Chrome(options=options)

    def _get_normal_driver(self):
        options = ChromeOptions()

        if self.headless:
            options.add_argument("--headless=new")
        if self.incognito:
            options.add_argument("--incognito")
        if self.proxy:
            options.add_argument(f"--proxy-server={self.proxy}")

        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-popup-blocking")
        options.add_argument("--disable-infobars")
        options.add_argument("--start-maximized")
        options.add_argument("--window-size=1920,1080")
        options.add_argument(f"user-agent={self.random_user_agent}")

        if self.use_seleniumwire:
            from seleniumwire import webdriver as wire_webdriver
            seleniumwire_options = {
                'proxy': {
                    'http': self.proxy,
                    'https': self.proxy,
                    'no_proxy': 'localhost,127.0.0.1'
                }
            } if self.proxy else {}
            return wire_webdriver.Chrome(options=options, seleniumwire_options=seleniumwire_options)
        else:
            return webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)





