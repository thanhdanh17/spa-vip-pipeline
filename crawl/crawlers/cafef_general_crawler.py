from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
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

def convert_date(date_str):
    formats = ["%d-%m-%Y - %H:%M %p", "%d-%m-%Y", "%d/%m/%Y"]
    for fmt in formats:
        try:
            dt = datetime.strptime(date_str.strip(), fmt)
            return format_datetime_for_db(dt)
        except:
            pass
    return None

def insert_to_supabase(db_manager, table_name, data):
    """Wrapper function để tương thích với code cũ - sử dụng hàm chung"""
    return insert_article_to_database(db_manager, table_name, data, convert_date)

def setup_driver():
    options = Options()
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--start-maximized")
    return webdriver.Chrome(options=options)

def extract_article_data(driver):
    soup = BeautifulSoup(driver.page_source, "html.parser")
    title = soup.select_one("h1.title")
    date_tag = soup.select_one("span.pdate[data-role='publishdate']")
    content_tag = soup.select_one("div.detail-content.afcbc-body")

    if not (title and date_tag and content_tag):
        return None

    content = " ".join(p.get_text(strip=True) for p in content_tag.select("p"))
    return {
        "title": title.get_text(strip=True),
        "date": date_tag.get_text(strip=True),
        "content": content,
        "link": driver.current_url,
        "ai_summary": None
    }

def click_view_more(driver, max_clicks=5):
    for i in range(max_clicks):
        try:
            driver.execute_script("window.scrollBy(0, 1200);")
            time.sleep(1)
            btn = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "div.btn-viewmore"))
            )
            driver.execute_script("arguments[0].scrollIntoView();", btn)
            time.sleep(0.5)
            btn.click()
            print(f"🔽 Click Xem thêm ({i+1}/{max_clicks})")
            time.sleep(2)
        except:
            print("⚠️ Không thấy nút Xem thêm nữa")
            break

def crawl_cafef_chung(max_clicks=5):
    driver = setup_driver()
    driver.get("https://cafef.vn/thi-truong-chung-khoan.chn")
    time.sleep(3)

    click_view_more(driver, max_clicks=max_clicks)

    links = driver.find_elements(By.CSS_SELECTOR, "div.tlitem.box-category-item h3 a")
    print(f"📄 Đã tìm thấy {len(links)} bài viết")

    all_data = []
    for i, link_el in enumerate(links):
        url = link_el.get_attribute("href")
        if not url: continue
        print(f"🔗 {url}")
        driver.execute_script("window.open(arguments[0]);", url)
        driver.switch_to.window(driver.window_handles[-1])
        time.sleep(1)
        data = extract_article_data(driver)
        if data: all_data.append(data)
        driver.close()
        driver.switch_to.window(driver.window_handles[0])
        time.sleep(1)

    driver.quit()

    db_manager = get_database_manager()
    for data in all_data:
        insert_to_supabase(db_manager, "General_News", data)
    db_manager.close_connections()
    print("🎉 Hoàn tất lưu vào Supabase!")

if __name__ == "__main__":
    crawl_cafef_chung(max_clicks=2)
