from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from datetime import datetime
import time

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

# ================== FORMAT NGÀY ==================
def convert_date(date_str):
    if not date_str or date_str.strip() == "":
        return None

    formats = [
        "%d-%m-%Y - %I:%M %p",  # 25-07-2025 - 05:52 PM
        "%d-%m-%Y - %H:%M %p",  # 25-07-2025 - 17:52 PM  (trường hợp giờ 24h + PM)
        "%d-%m-%Y",             # 25-07-2025
        "%d/%m/%Y",             # 25/07/2025
    ]

    for fmt in formats:
        try:
            dt = datetime.strptime(date_str.strip(), fmt)
            return format_datetime_for_db(dt)  # Sử dụng function từ database_config
        except:
            continue

    print(f"⚠️ Không parse được ngày: {date_str}")
    return None

# ================== HÀM INSERT CHỐNG TRÙNG ==================
def insert_to_supabase(db_manager, table_name, data):
    """Wrapper function để tương thích với code cũ - sử dụng hàm chung"""
    return insert_article_to_database(db_manager, table_name, data, convert_date)

# ================== HÀM SETUP SELENIUM ==================
def setup_driver():
    options = Options()
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--start-maximized")
    return webdriver.Chrome(options=options)

# ================== TRÍCH XUẤT DỮ LIỆU BÀI VIẾT ==================
def extract_article_data(driver):
    soup = BeautifulSoup(driver.page_source, "html.parser")
    try:
        title_tag = soup.select_one("h1.title")
        date_tag = soup.select_one("span.pdate[data-role='publishdate']")
        content_container = soup.select_one("div.detail-content.afcbc-body")

        if not (title_tag and date_tag and content_container):
            return None

        content = " ".join(p.get_text(strip=True) for p in content_container.select("p"))

        return {
            "title": title_tag.get_text(strip=True),
            "date": date_tag.get_text(strip=True),
            "content": content,
            "link": driver.current_url,
            "ai_summary": None  # Chưa có AI summary
        }
    except:
        return None

# ================== CRAWL THEO TỪ KHÓA ==================
def crawl_articles_sequentially(keyword="FPT", max_pages=1):
    driver = setup_driver()
    wait = WebDriverWait(driver, 10)
    results = []

    for page in range(1, max_pages + 1):
        search_url = f"https://cafef.vn/tim-kiem/trang-{page}.chn?keywords={keyword.replace(' ', '%20')}"
        print(f"\n🔎 Trang {page}: {search_url}")
        driver.get(search_url)
        time.sleep(2)

        article_links = driver.find_elements(By.CSS_SELECTOR, "div.item h3.titlehidden a")
        print(f"  👉 Tìm thấy {len(article_links)} bài viết")

        for index in range(len(article_links)):
            try:
                article_links = driver.find_elements(By.CSS_SELECTOR, "div.item h3.titlehidden a")
                link_el = article_links[index]
                driver.execute_script("arguments[0].scrollIntoView();", link_el)
                time.sleep(1)
                driver.execute_script("arguments[0].click();", link_el)
                time.sleep(2)

                wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "h1.title")))
                data = extract_article_data(driver)
                if data:
                    results.append(data)
                    print(f"✅ Lấy bài: {data['title'][:50]}...")

                driver.get(search_url)
                wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.item")))
                time.sleep(1)

            except Exception as e:
                print(f"❌ Lỗi tại bài {index+1}: {e}")
                driver.get(search_url)
                time.sleep(2)

    driver.quit()
    return results

# ================== MAIN ==================
def main_cafef():
    db_manager = get_database_manager()

    # Crawl theo keyword như cũ
    keyword_table_map = {
        "FPT": "FPT_News",
        "GAS": "GAS_News", 
        "IMP": "IMP_News",
        "VCB": "VCB_News",
    }
    
    for kw, table_name in keyword_table_map.items():
        print(f"\n🚀 Đang crawl keyword: {kw} -> Lưu vào {table_name}")
        articles = crawl_articles_sequentially(keyword=kw, max_pages=1)
        for article in articles:
            insert_to_supabase(db_manager, table_name, article)

    db_manager.close_connections()
    print("🎉 Hoàn tất lưu vào Supabase!")

if __name__ == "__main__":
   main_cafef()
