from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime, timedelta
from dateutil import parser
import time
import re

# Import centralized database system
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from database import SupabaseManager, DatabaseConfig, format_datetime_for_db

# Constants from old config
FIREANT_BASE_URL = "https://fireant.vn"
FIREANT_STOCK_URL = "https://fireant.vn/ma-chung-khoan"
FIREANT_ARTICLE_URL = "https://fireant.vn/bai-viet"
STOCK_CODES = ["FPT", "GAS", "IMP", "VCB"]

# Helper functions to replace old config functions
def get_database_manager():
    """Get database manager instance"""
    return SupabaseManager()

def get_table_name(stock_code=None, is_general=False):
    """Get table name using new config"""
    config = DatabaseConfig()
    return config.get_table_name(stock_code=stock_code, is_general=is_general)

def get_stock_url(stock_code):
    """Generate stock URL"""
    return f"{FIREANT_STOCK_URL}/{stock_code}"

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

# Configuration constants
MAX_SCROLLS = 5  # Số lần scroll 

def parse_fuzzy_datetime(raw_text, current_year):
    if not raw_text:
        return None
        
    raw_text = raw_text.strip()
    original_text = raw_text
    raw_text = raw_text.lower()
    
    try:
        if "hôm nay" in raw_text:
            time_part = raw_text.replace("hôm nay", "").strip()
            dt = datetime.strptime(time_part, "%H:%M")
            today = datetime.now()
            return today.replace(hour=dt.hour, minute=dt.minute, second=0, microsecond=0)

        if "hôm qua" in raw_text:
            time_part = raw_text.replace("hôm qua", "").strip()
            dt = datetime.strptime(time_part, "%H:%M")
            yesterday = datetime.now() - timedelta(days=1)
            return yesterday.replace(hour=dt.hour, minute=dt.minute, second=0, microsecond=0)

        # Xử lý "20 phút", "22 phút", "30 phút" trước
        match = re.match(r"(\d+)\s*phút", raw_text)
        if match:
            minutes_ago = int(match.group(1))
            return datetime.now() - timedelta(minutes=minutes_ago)

        elif "khoảng" in raw_text or "trước" in raw_text:
            return None 

        # Danh sách các format ngày có thể
        date_formats = [
            "%Y-%m-%d",           # 2025-08-02
            "%d/%m/%Y",           # 02/08/2025  
            "%d-%m-%Y",           # 02-08-2025
            "%d/%m %H:%M",        # 02/08 14:30
            "%d-%m-%Y %H:%M",     # 02-08-2025 14:30
            "%Y-%m-%d %H:%M:%S",  # 2025-08-02 14:30:00
        ]
        
        for fmt in date_formats:
            try:
                dt = datetime.strptime(original_text, fmt)
                # Nếu không có năm thì dùng current_year
                if "%Y" not in fmt:
                    dt = dt.replace(year=current_year)
                return dt
            except:
                continue
                
        # Nếu không match format nào thì return None
        return None

    except Exception as e:
        print(f"⚠️ Lỗi parse fuzzy time: '{original_text}' ({e})")
        return None

# def format_datetime_obj(dt):
#     return dt.strftime("%d-%m-%Y - %I:%M %p")

# def format_datetime_obj(dt):
#     day = dt.day
#     month = dt.month
#     year = dt.year
#     return f"{day}/{month}/{year}"

def format_datetime_obj(dt):
    return format_datetime_for_db(dt)

def fireant_date_parser(raw_text, current_year=2025):
    """Date parser cho FireAnt"""
    return parse_fuzzy_datetime(raw_text, current_year)


def setup_driver():
    options = Options()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-notifications")
    options.add_argument("--disable-infobars")
    options.add_argument("--disable-extensions")
    options.add_argument("--log-level=3")
    return webdriver.Chrome(options=options)

def scroll_and_collect_links(driver, stock_code="FPT", scroll_step=600):
    url = get_stock_url(stock_code)
    driver.get(url)
    time.sleep(5)

    links = []
    scroll_position = 0

    for i in range(MAX_SCROLLS):
        print(f"🔽 Scroll {i+1}/{MAX_SCROLLS}")
        scroll_position += scroll_step
        driver.execute_script(f"window.scrollTo(0, {scroll_position});")
        time.sleep(4)

        articles = driver.find_elements(By.CSS_SELECTOR, "div.flex.flex-row.h-full.border-b-1 a[href^='/bai-viet/']")
        for article in articles:
            try:
                href = article.get_attribute("href")
                if href and href.startswith("https://fireant.vn/bai-viet/"):
                    clean_href = href.split("?")[0]
                    if clean_href not in links:
                        links.append(clean_href)
            except:
                continue

        if scroll_position >= driver.execute_script("return document.body.scrollHeight"):
            break

    print(f"✅ Đã thu thập {len(links)} bài viết theo thứ tự từ trên xuống.")
    return links

def extract_article(driver, url):
    try:
        driver.get(url)
        time.sleep(3)
        soup = BeautifulSoup(driver.page_source, "html.parser")

        title_tag = soup.select_one("div.mt-3.mb-5.text-3xl.font-semibold.leading-10")
        title = title_tag.get_text(strip=True) if title_tag else ""

        fuzzy_time = ""
        dt = None

        time_tag = soup.select_one("time[datetime]")
        if time_tag:
            fuzzy_time = time_tag.get_text(strip=True)
            try:
                raw_iso = time_tag.get("datetime") or time_tag.get("title")
                if raw_iso:
                    dt = parser.parse(raw_iso)
            except Exception as e:
                print(f"⚠️ Lỗi parse ISO datetime: {e}")

        if not dt:
            fuzzy_tags = soup.select("span.text-gray-500")
            if fuzzy_tags:
                for tag in fuzzy_tags:
                    parts = tag.get_text(strip=True).split("|")
                    if len(parts) >= 1:
                        fuzzy_time = parts[-1].strip()  # Lấy phần cuối (thời gian)

        content_div = soup.find("div", id="post_content")
        content = ""
        if content_div:
            paragraphs = content_div.find_all("p")
            content = "\n".join(p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True))

        try:
            ai_button = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Tóm tắt tin tức bằng AI')]"))
            )
            ai_button.click()
            time.sleep(10)
            soup = BeautifulSoup(driver.page_source, "html.parser")
            ai_summary_tag = soup.select_one("div.italic:not(.font-bold)")
            ai_summary = ai_summary_tag.get_text(strip=True) if ai_summary_tag else ""
        except Exception as e:
            print(f"⚠️ AI summary lỗi: {e}")
            ai_summary = ""

        return {
            "title": title,
            "content": content,
            "link": url,
            "ai_summary": ai_summary,
            "fuzzy_time": fuzzy_time,
        }
    except Exception as e:
        print(f"❌ Lỗi khi crawl bài viết: {url} ({e})")
        return {}

def insert_to_supabase(db_manager, table_name, data):
    """Wrapper function để tương thích với code cũ - sử dụng hàm chung"""
    # Tạo date parser function cho FireAnt
    def fireant_date_parser_wrapper(date_str):
        dt = parse_fuzzy_datetime(date_str, 2025)
        return format_datetime_for_db(dt) if dt else None
    
    return insert_article_to_database(db_manager, table_name, data, fireant_date_parser_wrapper)

def crawl_fireant(stock_code="FPT", table_name="FPT_News"):
    db_manager = get_database_manager()

    driver = setup_driver()
    article_links = scroll_and_collect_links(driver, stock_code=stock_code)

    current_year = 2025
    base_day_month = None
    for idx, link in enumerate(article_links):
        print(f"📄 ({idx+1}/{len(article_links)}) {link}")
        raw_data = extract_article(driver, link)

        dt = parse_fuzzy_datetime(raw_data.get("fuzzy_time", ""), current_year)
        raw_data["date"] = format_datetime_obj(dt) if dt else ""

        insert_to_supabase(db_manager, table_name, raw_data)
    
    driver.quit()
    db_manager.close_connections()

def scroll_and_collect_general_articles(driver):
    url = FIREANT_ARTICLE_URL
    driver.get(url)
    time.sleep(5)

    links = []
    last_height = driver.execute_script("return document.body.scrollHeight")

    for i in range(MAX_SCROLLS):
        print(f"🔽 Scroll {i+1}/{MAX_SCROLLS}")
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(5)

        articles = driver.find_elements(By.CSS_SELECTOR, "a[href^='/bai-viet/']")
        for article in articles:
            try:
                href = article.get_attribute("href")
                if href and href.startswith("https://fireant.vn/bai-viet/"):
                    clean_href = href.split("?")[0]
                    if clean_href not in links:
                        links.append(clean_href)
            except:
                continue

        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

    print(f"✅ Thu thập {len(links)} bài viết từ {FIREANT_ARTICLE_URL}")
    return links

def crawl_fireant_general(table_name="General_News"):
    db_manager = get_database_manager()
    
    driver = setup_driver()
    article_links = scroll_and_collect_general_articles(driver)

    current_year = datetime.now().year

    for idx, link in enumerate(article_links):
        print(f"📄 ({idx+1}/{len(article_links)}) {link}")
        raw_data = extract_article(driver, link)

        # Ưu tiên parse fuzzy time
        dt = parse_fuzzy_datetime(raw_data.get("fuzzy_time", ""), current_year)

        # Nếu vẫn không có dt, thử parse trực tiếp từ raw_iso (nếu extract_article lấy được)
        if not dt:
            try:
                soup = BeautifulSoup(driver.page_source, "html.parser")
                time_tag = soup.select_one("time[datetime]")
                if time_tag:
                    raw_iso = time_tag.get("datetime") or time_tag.get("title")
                    if raw_iso:
                        dt = parser.parse(raw_iso)
            except:
                dt = None

        raw_data["date"] = format_datetime_obj(dt) if dt else datetime.now().strftime("%Y-%m-%d")

        insert_to_supabase(db_manager, table_name, raw_data)

    driver.quit()
    db_manager.close_connections()

def main_fireant():
    for code in STOCK_CODES:
        table_name = get_table_name(stock_code=code)
        crawl_fireant(stock_code=code, table_name=table_name)
    
    # Crawl tất cả bài viết chung
    general_table = get_table_name(is_general=True)
    crawl_fireant_general(table_name=general_table)

if __name__ == "__main__":
    main_fireant()

