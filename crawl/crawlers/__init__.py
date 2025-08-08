"""
Crawlers Package
Chứa tất cả các crawler cho các trang tin tức khác nhau
"""

from .fireant_crawler import crawl_fireant, crawl_fireant_general
from .cafef_keyword_crawler import main_cafef
from .cafef_general_crawler import crawl_cafef_chung
from .chungta_crawler import main_chungta

__all__ = [
    'crawl_fireant',
    'crawl_fireant_general', 
    'main_cafef',
    'crawl_cafef_chung',
    'main_chungta'
]
