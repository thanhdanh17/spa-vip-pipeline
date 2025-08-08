#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Main Crawler Controller
Chạy tất cả các crawler theo luồng có tổ chức
Author: Auto-generated
Date: August 3, 2025
"""

import sys
import os
import time
import logging
from datetime import datetime
from typing import List, Dict, Callable

# Import các crawler modules
from crawlers.fireant_crawler import crawl_fireant, crawl_fireant_general
from crawlers.cafef_keyword_crawler import main_cafef
from crawlers.cafef_general_crawler import crawl_cafef_chung
from crawlers.chungta_crawler import main_chungta

# Import centralized database system
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import SupabaseManager

# Helper function for compatibility
def get_database_manager():
    """Get database manager instance"""
    return SupabaseManager()

# Import stock crawler
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'crawl_stock'))
from crawl_stock.crawl_stock_price_history import main_stock_simplize

# Cấu hình logging với UTF-8 encoding cho Windows
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'logs/crawl_log_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

class CrawlerController:
    """Controller để quản lý và chạy tất cả các crawler"""
    
    def __init__(self):
        self.start_time = None
        self.crawlers_status = {}
        
    def log_start(self, crawler_name: str):
        """Ghi log bắt đầu crawler"""
        logger.info(f"[START] Bắt đầu {crawler_name}")
        self.crawlers_status[crawler_name] = {
            'start_time': datetime.now(),
            'status': 'running'
        }
        
    def log_success(self, crawler_name: str):
        """Ghi log thành công"""
        end_time = datetime.now()
        start_time = self.crawlers_status[crawler_name]['start_time']
        duration = end_time - start_time
        
        self.crawlers_status[crawler_name].update({
            'end_time': end_time,
            'status': 'success',
            'duration': duration
        })
        
        logger.info(f"[SUCCESS] {crawler_name} hoàn thành trong {duration}")
        
    def log_error(self, crawler_name: str, error: Exception):
        """Ghi log lỗi"""
        end_time = datetime.now()
        start_time = self.crawlers_status[crawler_name]['start_time']
        duration = end_time - start_time
        
        self.crawlers_status[crawler_name].update({
            'end_time': end_time,
            'status': 'error',
            'duration': duration,
            'error': str(error)
        })
        
        logger.error(f"[ERROR] {crawler_name} lỗi sau {duration}: {error}")
        
    def run_crawler(self, crawler_func: Callable, crawler_name: str, *args, **kwargs):
        """Chạy một crawler với error handling"""
        try:
            self.log_start(crawler_name)
            result = crawler_func(*args, **kwargs)
            self.log_success(crawler_name)
            return result
        except Exception as e:
            self.log_error(crawler_name, e)
            return None
            
    def run_fireant_crawlers(self):
        """Chạy các crawler FireAnt"""
        logger.info("=== FIREANT CRAWLERS ===")
        
        # Crawler cho tất cả mã cổ phiếu
        stock_codes = ["FPT", "GAS", "IMP", "VCB"]
        for stock_code in stock_codes:
            self.run_crawler(
                crawl_fireant, 
                f"FireAnt {stock_code} Stock", 
                stock_code=stock_code, 
                table_name=f"{stock_code}_News"
            )
        
        # Crawler cho tin tức tổng quát FireAnt
        self.run_crawler(
            crawl_fireant_general,
            "FireAnt General News",
            table_name="General_News"
        )
        
    def run_cafef_crawlers(self):
        """Chạy các crawler CafeF"""
        logger.info("=== CAFEF CRAWLERS ===")
        
        # CafeF crawler với từ khóa
        self.run_crawler(
            main_cafef,
            "CafeF Keyword Search"
        )
        
        # CafeF crawler chung
        self.run_crawler(
            crawl_cafef_chung,
            "CafeF General News",
            max_clicks=5
        )
        
    def run_chungta_crawler(self):
        """Chạy crawler ChungTa"""
        logger.info("=== CHUNGTA CRAWLER ===")
        
        self.run_crawler(
            main_chungta,
            "ChungTa News"
        )
        
    def run_stock_crawler(self):
        """Chạy crawler Stock Price"""
        logger.info("=== STOCK PRICE CRAWLER ===")
        
        self.run_crawler(
            main_stock_simplize,
            "Stock Price Crawler"
        )
        
    def print_summary(self):
        """In báo cáo tổng kết"""
        logger.info("\n" + "="*60)
        logger.info("TONG KET CRAWLING SESSION")
        logger.info("="*60)
        
        total_duration = datetime.now() - self.start_time
        successful = sum(1 for status in self.crawlers_status.values() if status['status'] == 'success')
        failed = sum(1 for status in self.crawlers_status.values() if status['status'] == 'error')
        
        logger.info(f"Tong thoi gian: {total_duration}")
        logger.info(f"Thanh cong: {successful}")
        logger.info(f"That bai: {failed}")
        logger.info(f"Tong crawler: {len(self.crawlers_status)}")
        
        logger.info("\nChi tiet tung crawler:")
        for name, status in self.crawlers_status.items():
            status_icon = "[OK]" if status['status'] == 'success' else "[FAIL]"
            duration = status.get('duration', 'N/A')
            logger.info(f"{status_icon} {name}: {duration}")
            
            if status['status'] == 'error':
                logger.info(f"   Loi: {status.get('error', 'Unknown error')}")
                
    def run_all_crawlers(self):
        """Chạy tất cả các crawler theo luồng"""
        self.start_time = datetime.now()
        
        logger.info("=" * 50)
        logger.info("BAT DAU CRAWLING SESSION")
        logger.info("=" * 50)
        logger.info(f"Thoi gian bat dau: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        try:
            # 1. Chạy Stock Price crawler đầu tiên
            self.run_stock_crawler()
            time.sleep(2)  # Nghỉ giữa các session
            
            # 2. Chạy FireAnt crawlers
            self.run_fireant_crawlers()
            time.sleep(2)
            
            # 3. Chạy CafeF crawlers  
            self.run_cafef_crawlers()
            time.sleep(2)
            
            # 4. Chạy ChungTa crawler
            self.run_chungta_crawler()
            
        except KeyboardInterrupt:
            logger.warning("Nguoi dung dung crawling session")
        except Exception as e:
            logger.error(f"Loi nghiem trong trong crawling session: {e}")
        finally:
            self.print_summary()

def run_single_crawler(crawler_name: str):
    """Chạy một crawler đơn lẻ"""
    controller = CrawlerController()
    
    crawler_map = {
        'fireant_fpt': lambda: crawl_fireant(stock_code="FPT", table_name="FPT_News"),
        'fireant_gas': lambda: crawl_fireant(stock_code="GAS", table_name="GAS_News"),
        'fireant_imp': lambda: crawl_fireant(stock_code="IMP", table_name="IMP_News"),
        'fireant_vcb': lambda: crawl_fireant(stock_code="VCB", table_name="VCB_News"),
        'fireant_general': lambda: crawl_fireant_general(table_name="General_News"),
        'cafef_keyword': main_cafef,
        'cafef_general': lambda: crawl_cafef_chung(max_clicks=5),
        'chungta': main_chungta,
        'stock_price': main_stock_simplize
    }
    
    if crawler_name not in crawler_map:
        logger.error(f"Khong tim thay crawler: {crawler_name}")
        logger.info(f"Cac crawler co san: {list(crawler_map.keys())}")
        return
        
    controller.start_time = datetime.now()
    controller.run_crawler(crawler_map[crawler_name], crawler_name.title())
    controller.print_summary()

def main_crawl():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='News Crawler Controller')
    parser.add_argument('--single', '-s', help='Chạy một crawler đơn lẻ', 
                       choices=['fireant_fpt', 'fireant_gas', 'fireant_imp', 'fireant_vcb', 'fireant_general', 'cafef_keyword', 'cafef_general', 'chungta', 'stock_price'])
    parser.add_argument('--list', '-l', action='store_true', help='Liệt kê các crawler có sẵn')
    
    args = parser.parse_args()
    
    if args.list:
        print("Cac crawler co san:")
        print("  - fireant_fpt: FireAnt FPT stock news")
        print("  - fireant_gas: FireAnt GAS stock news")
        print("  - fireant_imp: FireAnt IMP stock news")
        print("  - fireant_vcb: FireAnt VCB stock news")
        print("  - fireant_general: FireAnt general news")
        print("  - cafef_keyword: CafeF keyword search")
        print("  - cafef_general: CafeF general news")
        print("  - chungta: ChungTa news")
        print("  - stock_price: Stock price history from Simplize")
        return
        
    if args.single:
        run_single_crawler(args.single)
    else:
        # Chạy tất cả crawler
        controller = CrawlerController()
        controller.run_all_crawlers()

if __name__ == "__main__":
    main_crawl()
