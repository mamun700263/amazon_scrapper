import csv
import json
import random
import sqlite3
import time
from typing import List, Dict, Optional

import pandas as pd
import requests
from bs4 import BeautifulSoup
from logger import logger


def soup_maker(response: str) -> Optional[BeautifulSoup]:
    """
    Converts a response to a BeautifulSoup object for parsing HTML.
    """
    try:
        soup = BeautifulSoup(response, "lxml")
        logger.info("✅ Soup created successfully")
        return soup
    except Exception as e:
        logger.error(f"❌ Failed to create soup: {e}")
        return None


def scroll_and_wait(driver, wait_time: int = 2, scroll_pause: float = 0.5, max_scrolls: int = 10) -> None:
    """
    Scrolls the page down until the end or max_scrolls is reached.
    """
    last_height = driver.execute_script("return document.body.scrollHeight")

    for _ in range(max_scrolls):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(scroll_pause)

        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height
        logger.debug(f"🔁 Scrolled to height: {new_height}")

    time.sleep(wait_time)


def load_and_scroll(driver, url: str) -> None:
    """
    Loads a page and performs scrolling to ensure content is fully loaded.
    """
    try:
        logger.info(f"🌐 Navigating to: {url}")
        driver.get(url)
        sleeper()
        scroll_and_wait(driver)
    except Exception as e:
        logger.error(f"❌ Failed to load {url}: {e}")


def sleeper(minimum: float = 3, maximum: float = 8) -> None:
    """
    Sleeps for a random time between minimum and maximum.
    """
    x = random.uniform(minimum, maximum)
    logger.debug(f"⏱️ Sleeping for {x:.2f} seconds...")
    time.sleep(x)


def file_format_checker(file_name: str) -> str:
    """
    Checks the file format based on the file extension.
    """
    file_name = file_name.lower()
    if file_name.endswith(".csv"):
        return "csv"
    elif file_name.endswith(".json"):
        return "json"
    elif file_name.endswith(".xlsx"):
        return "xlsx"
    elif file_name.endswith(".sqlite"):
        return "sqlite"
    else:
        raise ValueError("Invalid file format. Use .csv, .json, or .xlsx.")


def save_as(items: List[Dict[str, str]], file_name: Optional[str] = None, post_api_url: Optional[str] = None, table_name: str = "products") -> None:
    """
    Saves data to the specified format (CSV, JSON, Excel, SQLite) or POSTs it to an API.
    """
    if not items:
        logger.warning("⚠️ No items to save.")
        return

    # First, POST the data to the API if we have the URL
    if post_api_url:
        try:
            if post_with_retry(post_api_url, items):
                return
            else:
                return
        except Exception as e:
            logger.error(f"❌ Exception while POSTing to API: {e}")
        return  # Stop here if only posting to the API (do not save to file)
    
    try:
        file_ext = file_format_checker(file_name)
    except ValueError as e:
        logger.error(f"❌ {e}")
        return

    # Otherwise, save data to file if no post_api_url was provided
    if not file_name:
        logger.warning("⚠️ No file name provided and no API endpoint.")
        return

    try:
        if file_ext == "csv":
            with open(file_name, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=items[0].keys())
                writer.writeheader()
                writer.writerows(items)
            logger.info(f"✅ Data saved as CSV: {file_name}")

        elif file_ext == "json":
            with open(file_name, "w", encoding="utf-8") as f:
                json.dump(items, f, ensure_ascii=False, indent=4)
            logger.info(f"✅ Data saved as JSON: {file_name}")

        elif file_ext in ["xlsx", "xls"]:
            df = pd.DataFrame(items)
            df.to_excel(file_name, index=False)
            logger.info(f"✅ Data saved as Excel: {file_name}")

        elif file_ext == "sqlite":
            save_to_sqlite(items, file_name, table_name)
    except Exception as e:
        logger.error(f"❌ Failed to save data: {e}")


def save_to_sqlite(items: List[Dict[str, str]], db_name: str, table_name: str = "products") -> None:
    """
    Saves data to an SQLite database.
    """
    try:
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()

        columns = ", ".join([f"{key} TEXT" for key in items[0].keys()])
        cursor.execute(f"CREATE TABLE IF NOT EXISTS {table_name} ({columns})")

        for item in items:
            placeholders = ", ".join(["?"] * len(item))
            values = tuple(item.values())
            cursor.execute(f"INSERT INTO {table_name} VALUES ({placeholders})", values)

        conn.commit()
        conn.close()
        logger.info(f"✅ Data saved to SQLite: {db_name} → {table_name}")
    except Exception as e:
        logger.error(f"❌ Failed to save to SQLite: {e}")


def post_with_retry(url: str, data: List[Dict[str, str]], max_retries: int = 3, delay: int = 2, timeout: int = 10) -> bool:
    """
    Attempts to POST data to the given URL with retry logic.
    Returns True if successful, False otherwise.
    """
    for attempt in range(1, max_retries + 1):
        try:
            res = requests.post(url, json=data, timeout=timeout)
            if res.status_code in [200, 201]:
                logger.info(f"✅ Data successfully POSTed to API on attempt {attempt}")
                return True
            else:
                logger.warning(f"⚠️ Attempt {attempt}: API POST failed ({res.status_code}) - {res.text}")
        except requests.exceptions.RequestException as e:
            logger.warning(f"⚠️ Attempt {attempt}: Exception during POST - {e}")

        time.sleep(delay)

    logger.error("❌ All retry attempts for API POST failed.")
    return False
