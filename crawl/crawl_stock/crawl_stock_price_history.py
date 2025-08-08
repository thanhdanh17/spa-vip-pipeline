from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pandas as pd
from datetime import datetime
import sys
import os

# Import centralized database system
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from database import SupabaseManager, DatabaseConfig

# Helper functions
def get_database_manager():
    """Get database manager instance"""
    return SupabaseManager()

# 🔹 Chuyển đổi định dạng ngày cho Supabase
def convert_date_for_supabase(date_str):
    """Chuyển đổi định dạng ngày từ DD/MM/YYYY sang YYYY-MM-DD cho Supabase"""
    try:
        # 🔧 FIX: Xử lý nhiều format ngày khác nhau
        if not date_str or date_str.strip() == "" or date_str.strip() == "-":
            print(f"❌ Lỗi format ngày: empty string")
            return None
            
        date_str = date_str.strip()
        
        # Thử format DD/MM/YYYY
        try:
            dt = datetime.strptime(date_str, "%d/%m/%Y")
            return dt.strftime("%Y-%m-%d")
        except ValueError:
            pass
            
        # Thử format DD-MM-YYYY  
        try:
            dt = datetime.strptime(date_str, "%d-%m-%Y")
            return dt.strftime("%Y-%m-%d")
        except ValueError:
            pass
            
        # Thử format YYYY-MM-DD (đã đúng format)
        try:
            dt = datetime.strptime(date_str, "%Y-%m-%d")
            return dt.strftime("%Y-%m-%d")
        except ValueError:
            pass
            
        print(f"❌ Lỗi format ngày: {date_str} (không match format nào)")
        return None
        
    except Exception as e:
        print(f"❌ Lỗi format ngày: {date_str} - {e}")
        return None


# 🔹 Hàm upsert (insert hoặc update) với Supabase API  
def upsert_stock_data(db_manager, table_name, row):
    """
    Insert hoặc Update dữ liệu stock vào Supabase
    - Nếu ngày chưa tồn tại: INSERT mới
    - Nếu ngày đã tồn tại: UPDATE với giá trị mới
    """
    try:
        formatted_date = convert_date_for_supabase(row["date"])
        if not formatted_date:
            print(f"❌ Lỗi format ngày: {row['date']}")
            return

        # Hàm helper để chuyển đổi giá sang float
        def safe_float(value_str):
            """Chuyển đổi chuỗi số có dấu phẩy thành float"""
            if not value_str or value_str == "" or value_str == "-":
                return 0.0
            return float(str(value_str).replace(",", ""))

        # Chuẩn bị dữ liệu
        data_to_upsert = {
            "date": formatted_date,
            "open_price": f"{safe_float(row['open_price']):,.0f}" if safe_float(row["open_price"]) > 0 else "EMPTY",
            "high_price": f"{safe_float(row['high_price']):,.0f}" if safe_float(row["high_price"]) > 0 else "EMPTY", 
            "low_price": f"{safe_float(row['low_price']):,.0f}" if safe_float(row["low_price"]) > 0 else "EMPTY",
            "close_price": f"{safe_float(row['close_price']):,.0f}" if safe_float(row["close_price"]) > 0 else "EMPTY",
            "change": row["change"],
            "change_pct": row["change_pct"],
            "volume": row["volume"]
        }

        supabase_client = db_manager.get_supabase_client()
        
        # Kiểm tra dữ liệu đã tồn tại theo ngày
        existing = supabase_client.table(table_name).select("*").eq("date", formatted_date).execute()
        
        if existing.data:
            # CẬP NHẬT dữ liệu hiện có
            existing_record = existing.data[0]
            
            # So sánh để xem có thay đổi không (sử dụng safe comparison)
            def safe_compare(existing_val, new_val):
                """So sánh an toàn giữa giá trị cũ và mới"""
                try:
                    # Nếu existing_val là string có dấu phẩy, xóa dấu phẩy trước khi so sánh
                    if isinstance(existing_val, str) and existing_val != "EMPTY":
                        existing_float = float(existing_val.replace(",", ""))
                    else:
                        existing_float = float(existing_val) if existing_val and existing_val != "EMPTY" else 0.0
                    
                    # Nếu new_val là string có dấu phẩy, xóa dấu phẩy
                    if isinstance(new_val, str) and new_val != "EMPTY":
                        new_float = float(new_val.replace(",", ""))
                    else:
                        new_float = float(new_val) if new_val and new_val != "EMPTY" else 0.0
                        
                    return existing_float != new_float
                except (ValueError, TypeError):
                    return True  # Nếu không convert được thì coi như có thay đổi
            
            needs_update = (
                safe_compare(existing_record.get('close_price', 0), data_to_upsert['close_price']) or
                safe_compare(existing_record.get('open_price', 0), data_to_upsert['open_price']) or
                safe_compare(existing_record.get('high_price', 0), data_to_upsert['high_price']) or
                safe_compare(existing_record.get('low_price', 0), data_to_upsert['low_price'])
            )
            
            if needs_update:
                result = supabase_client.table(table_name).update(data_to_upsert).eq("date", formatted_date).execute()
                if result.data:
                    print(f"🔄 Đã cập nhật: {row['date']} - {data_to_upsert['close_price']} (Giá thay đổi)")
                else:
                    print(f"❌ Lỗi khi cập nhật: {row['date']}")
            else:
                print(f"⏩ Không thay đổi: {row['date']} - {data_to_upsert['close_price']}")
        else:
            # THÊM MỚI dữ liệu
            result = supabase_client.table(table_name).insert(data_to_upsert).execute()
            
            if result.data:
                print(f"✅ Đã thêm mới: {row['date']} - {data_to_upsert['close_price']}")
            else:
                print(f"❌ Lỗi khi thêm: {row['date']}")
                
    except Exception as e:
        print(f"❌ Lỗi upsert_stock_data: {e}")
        print(f"   Dữ liệu: {row}")

def setup_driver():
    """Setup Chrome driver với các options tối ưu"""
    options = Options()
    options.add_argument("--headless")  # Chạy ẩn browser
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    
    return webdriver.Chrome(options=options)

# 🔹 Crawl từng trang và lưu ngay vào Supabase
def crawl_and_save_stock(stock_code, max_pages=5):
    """
    Crawl dữ liệu cổ phiếu từ Simplize và lưu vào Supabase
    """
    print(f"🚀 Bắt đầu crawl {stock_code} với {max_pages} trang...")
    
    driver = setup_driver()
    db_manager = get_database_manager()

    url = f"https://simplize.vn/co-phieu/{stock_code}/lich-su-gia"
    driver.get(url)
    wait = WebDriverWait(driver, 10)
    time.sleep(2)

    table_name = f"{stock_code}_Stock"

    try:
        for page in range(1, max_pages + 1):
            print(f"🔍 Crawling {stock_code} - Trang {page}...")
            time.sleep(2)

            # 🔧 FIX: Sử dụng logic từ fix_simplize_crawl.py để khắc phục virtual DOM
            try:
                # Đợi table load
                wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "tr.simplize-table-row-level-0")))
                
                # Lấy tất cả rows sử dụng CSS selector chính xác từ fix
                rows = driver.find_elements(By.CSS_SELECTOR, "tr.simplize-table-row-level-0")
                
                for row in rows:
                    try:
                        # 🔧 FIX: Scroll từng dòng để đảm bảo dòng nằm trong viewport
                        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", row)
                        time.sleep(0.1)  # Cho DOM kịp render

                        # Lấy dữ liệu từ dòng hiện tại
                        cols = row.find_elements(By.CSS_SELECTOR, "td")
                        if len(cols) >= 8:
                            # 🔧 FIX: Lấy text từ h6 element như trong fix_simplize_crawl.py
                            date = cols[0].find_element(By.TAG_NAME, "h6").text.strip()
                            values = []
                            
                            for i in range(1, 8):
                                try:
                                    val = cols[i].find_element(By.TAG_NAME, "h6").text.strip()
                                except:
                                    val = "-"
                                values.append(val)

                            data_row = {
                                "date": date,               # Ngày
                                "open_price": values[0],    # Giá mở cửa
                                "high_price": values[1],    # Giá cao nhất
                                "low_price": values[2],     # Giá thấp nhất
                                "close_price": values[3],   # Giá đóng cửa
                                "change": values[4],        # Thay đổi giá
                                "change_pct": values[5],    # % Thay đổi
                                "volume": values[6]         # Khối lượng
                            }

                            upsert_stock_data(db_manager, table_name, data_row)
                            
                    except Exception as e:
                        print(f"❌ Lỗi dòng: {e}")
                        continue

            except Exception as e:
                print(f"❌ Không lấy được dữ liệu trang {page} cho mã {stock_code}: {e}")
                break

            # Sang trang tiếp theo - 🔧 FIX: Sử dụng xpath như trong fix_simplize_crawl.py
            if page < max_pages:
                try:
                    next_btn = driver.find_element(By.XPATH, f'//a[text()="{page + 1}"]')
                    driver.execute_script("arguments[0].click();", next_btn)
                    time.sleep(2)
                except Exception as e:
                    print(f"⚠️ Không thể click sang trang {page+1}: {e}")
                    break

    except Exception as e:
        print(f"❌ Lỗi trong quá trình crawl: {e}")
    finally:
        driver.quit()
        db_manager.close_connections()
        print(f"✅ Hoàn tất lưu dữ liệu cho {stock_code}")

def main_stock_simplize():
    """Hàm chính để crawl nhiều mã cổ phiếu"""
    stock_codes = ["FPT","GAS","VCB","IMP"]  # ✅ Test với 1 mã trước

    for code in stock_codes:
        try:
            crawl_and_save_stock(code, max_pages=1)
            time.sleep(5)  # Nghỉ giữa các mã cổ phiếu
        except Exception as e:
            print(f"❌ Lỗi khi crawl {code}: {e}")
            continue

if __name__ == "__main__":
    main_stock_simplize()
