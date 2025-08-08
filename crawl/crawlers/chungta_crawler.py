from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
import requests
import re
from datetime import datetime

# Import centralized database system
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from database import SupabaseManager, DatabaseConfig, format_datetime_for_db

# Constants
STOCK_CODES = ["FPT", "GAS", "IMP", "VCB"]

# Helper functions
def get_database_manager():
    """Get database manager instance"""
    return SupabaseManager()

def get_table_name(stock_code=None, is_general=False):
    """Get table name using new config"""
    config = DatabaseConfig()
    return config.get_table_name(stock_code=stock_code, is_general=is_general)

def insert_article_to_database(db_manager, table_name, article_data, date_parser_func=None):
    """Insert article using new database system"""
    # Parse date if parser provided
    if date_parser_func and article_data.get("date"):
        try:
            parsed_date = date_parser_func(article_data["date"])
            if parsed_date:
                article_data["date"] = parsed_date
        except Exception:
            pass
    
    return db_manager.insert_article(table_name, article_data)

def normalize_date_only(raw_text):
    if not raw_text or raw_text.strip() == "" or raw_text.strip().upper() == "EMPTY":
        return None

    raw_text = raw_text.strip()

    # Trường hợp dạng 23-07-2025 - 06:57 AM
    try:
        dt = datetime.strptime(raw_text, "%d-%m-%Y - %I:%M %p")
        return format_datetime_for_db(dt)
    except:
        pass

    # Trường hợp dạng Thứ sáu, 25/7/2025 | 18:08GMT hoặc 30/7/2025
    try:
        match = re.search(r"(\d{1,2})/(\d{1,2})/(\d{4})", raw_text)
        if match:
            day, month, year = match.groups()
            dt = datetime(int(year), int(month), int(day))
            return format_datetime_for_db(dt)
    except:
        pass
    return None

# 🔹 Crawl dữ liệu từ Chungta.vn
def crawl_chungta(url):
    options = Options()
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    driver = webdriver.Chrome(options=options)

    driver.get(url)
    wait = WebDriverWait(driver, 10)

    MAX_PAGE = 2

    for _ in range(MAX_PAGE):
        try:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            button = wait.until(EC.element_to_be_clickable((By.ID, "load_more_redesign")))
            button.click()
            time.sleep(4)
        except:
            print("⚠️ Không thể click hoặc hết bài.")
            break

    soup = BeautifulSoup(driver.page_source, "html.parser")
    driver.quit()

    articles = soup.select("h3.title-news a")
    print(f"Tìm thấy {len(articles)} bài viết.")

    results = []
    headers = {"User-Agent": "Mozilla/5.0"}

    for a in articles:
        title_preview = a.get_text(strip=True)
        link = "https://chungta.vn" + a.get("href")

        try:
            res = requests.get(link, headers=headers, timeout=10)
            article_soup = BeautifulSoup(res.text, "html.parser")

            title = article_soup.select_one("h1.title-detail")
            title = title.get_text(strip=True) if title else title_preview

            date = article_soup.select_one("span.time")
            date = date.get_text(strip=True) if date else "Không rõ ngày"

            content = article_soup.select_one("article.fck_detail.width_common")
            content = content.get_text(separator="\n", strip=True) if content else ""

            results.append({
                "title": title,
                "date": date,
                "link": link,
                "content": content,
                "ai_summary": "" 
            })

            print(f"✅ Crawled: {title}")

        except Exception as e:
            print(f"❌ Lỗi lấy bài {link}: {e}")

    return results

def main_chungta():
    urls = [
        "https://chungta.vn/kinh-doanh",
        "https://chungta.vn/cong-nghe"
    ]
    table_name = "FPT_News"  # Chung Ta lưu vào FPT_News vì có nhiều tin về FPT
    db_manager = get_database_manager()

    for url in urls:
        articles = crawl_chungta(url) 
        for article in articles:
            # Sử dụng hàm chung từ database_config
            insert_article_to_database(db_manager, table_name, article, normalize_date_only)
        print(f"🎉 Hoàn tất lưu vào {table_name} từ {url}")

    db_manager.close_connections()

if __name__ == "__main__":
    main_chungta()