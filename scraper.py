#!/usr/bin/env python3
"""Scrape Shanghai Xingjiao Education news and persist them into MySQL."""

import re
import sys
import time
from typing import Dict, List, Optional
from urllib.parse import urljoin

import pymysql
import requests
from bs4 import BeautifulSoup
from pymysql import MySQLError
from requests.adapters import HTTPAdapter
from requests.exceptions import RequestException
from urllib3.util.retry import Retry

from config import (
    BASE_URL,
    DB_CONFIG,
    PAGE_URL_TEMPLATE,
    REQUEST_DELAY,
    SITE_ROOT,
    USER_AGENT,
)


class NewsScraper:
    """Scraper responsible for crawling list pages and saving articles."""

    def __init__(self) -> None:
        self.delay: float = max(float(REQUEST_DELAY), 0.5)
        self.session: requests.Session = self._init_session()
        self.db_connection: Optional[pymysql.connections.Connection] = None
        self.cursor: Optional[pymysql.cursors.Cursor] = None

    @staticmethod
    def _init_session() -> requests.Session:
        session = requests.Session()
        session.headers.update({"User-Agent": USER_AGENT})

        retries = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=(500, 502, 503, 504),
            allowed_methods=frozenset(["GET"]),
        )
        adapter = HTTPAdapter(max_retries=retries)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        return session

    def connect_db(self) -> None:
        try:
            self.db_connection = pymysql.connect(**DB_CONFIG)
            self.cursor = self.db_connection.cursor()
            print(f"✓ Connected to database: {DB_CONFIG['database']}")
        except MySQLError as exc:
            print(f"✗ Unable to connect to database: {exc}")
            self.close()
            sys.exit(1)

    def close(self) -> None:
        if self.cursor:
            self.cursor.close()
            self.cursor = None
        if self.db_connection:
            self.db_connection.close()
            self.db_connection = None
            print("✓ Database connection closed")
        if self.session:
            self.session.close()

    def fetch_url(self, url: str) -> Optional[str]:
        try:
            response = self.session.get(url, timeout=20)
            response.raise_for_status()
        except RequestException as exc:
            print(f"  Warning: Failed to fetch {url}: {exc}")
            return None

        response.encoding = response.apparent_encoding or response.encoding or "utf-8"
        return response.text

    def get_total_pages(self) -> int:
        html = self.fetch_url(BASE_URL)
        if not html:
            print("✗ Unable to fetch the first page; defaulting to a single page")
            return 1

        soup = BeautifulSoup(html, "lxml")
        last_page_link = soup.select_one("a.last[href*='list']")

        if last_page_link and last_page_link.has_attr("href"):
            match = re.search(r"list(\d+)\.htm", last_page_link["href"])
            if match:
                total_pages = int(match.group(1))
                print(f"✓ Detected {total_pages} pages in total")
                return total_pages

        print("✓ Detected a single list page")
        return 1

    def extract_news_list(self, html: str) -> List[Dict[str, str]]:
        soup = BeautifulSoup(html, "lxml")
        news_items: List[Dict[str, str]] = []

        for li in soup.select("ul.news_list li.news"):
            link_elem = li.select_one(".news_title a")
            if not link_elem or not link_elem.get("href"):
                continue

            title = link_elem.get_text(strip=True)
            href = link_elem.get("href", "").strip()
            if not title or not href:
                continue

            full_url = urljoin(SITE_ROOT, href)
            news_items.append({"title": title, "url": full_url})

        return news_items

    def extract_article_content(self, url: str) -> Optional[Dict[str, str]]:
        html = self.fetch_url(url)
        if not html:
            print(f"  Warning: Skipping article due to fetch failure: {url}")
            return None

        soup = BeautifulSoup(html, "lxml")

        title_elem = soup.select_one(".arti_title") or soup.select_one(".art_title")
        if title_elem:
            title = title_elem.get_text(strip=True)
        else:
            title_tag = soup.select_one("title")
            title = title_tag.get_text(strip=True) if title_tag else ""

        content_elem = soup.select_one(".wp_articlecontent")
        if not content_elem:
            print(f"  Warning: Content block not found for {url}")
            return None

        content_text = content_elem.get_text("\n", strip=True)
        if not content_text:
            print(f"  Warning: Empty content for {url}")
            return None

        return {
            "title": title or "未命名文章",
            "content": content_text,
            "url": url,
        }

    def save_article(self, article: Dict[str, str]) -> bool:
        if not self.cursor or not self.db_connection:
            raise RuntimeError("Database connection is not initialized.")

        try:
            sql = (
                "INSERT INTO news_articles (title, url, content) "
                "VALUES (%s, %s, %s) "
                "ON DUPLICATE KEY UPDATE title = VALUES(title), content = VALUES(content)"
            )
            self.cursor.execute(sql, (article["title"], article["url"], article["content"]))
            self.db_connection.commit()
            return True
        except MySQLError as exc:
            print(f"  ✗ Failed to save article '{article['title']}': {exc}")
            self.db_connection.rollback()
            return False

    def scrape_page(self, page_num: int) -> int:
        page_url = BASE_URL if page_num == 1 else PAGE_URL_TEMPLATE.format(page=page_num)
        print(f"\nScraping page {page_num}: {page_url}")

        html = self.fetch_url(page_url)
        if not html:
            print(f"  ✗ Failed to load page {page_num}")
            return 0

        news_items = self.extract_news_list(html)
        print(f"  Found {len(news_items)} article links on page {page_num}")

        saved_count = 0
        for index, item in enumerate(news_items, start=1):
            print(f"  [{index}/{len(news_items)}] Fetching article: {item['title'][:50]}")
            article = self.extract_article_content(item["url"])
            if article and self.save_article(article):
                saved_count += 1
                print("    ✓ Article saved")
            time.sleep(self.delay)

        return saved_count

    def run(self) -> None:
        print("=" * 60)
        print("Shanghai Xingjiao Education News Scraper")
        print("=" * 60)

        self.connect_db()
        total_pages = self.get_total_pages()
        total_saved = 0

        try:
            for page_num in range(1, total_pages + 1):
                saved_count = self.scrape_page(page_num)
                total_saved += saved_count
                if page_num < total_pages:
                    print(f"\n  Waiting {self.delay} seconds before the next page...")
                    time.sleep(self.delay)
        finally:
            self.close()

        print("\n" + "=" * 60)
        print("Scraping completed")
        print(f"Total pages scraped: {total_pages}")
        print(f"Total articles inserted/updated: {total_saved}")
        print("=" * 60)


def main() -> None:
    scraper = NewsScraper()
    try:
        scraper.run()
    except KeyboardInterrupt:
        print("\nScraping interrupted by user")
        scraper.close()
        sys.exit(0)
    except Exception as exc:  # pylint: disable=broad-except
        print(f"\nFatal error: {exc}")
        scraper.close()
        raise


if __name__ == "__main__":
    main()
