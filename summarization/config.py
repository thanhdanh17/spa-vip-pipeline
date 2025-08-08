import os
import sys
import torch
import importlib.util
from dotenv import load_dotenv
from typing import Dict, Any
from pathlib import Path

# Thêm đường dẫn để import config từ thư mục crawl
crawl_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'crawl')
if crawl_path not in sys.path:
    sys.path.insert(0, crawl_path)

# Import constants từ shared config để tránh conflicts
try:
    from .shared_config import (
        DEFAULT_SUPABASE_URL, 
        DEFAULT_SUPABASE_KEY, 
        TABLE_NAMES, 
        STOCK_CODES
    )
except ImportError:
    # Fallback if relative import fails
    current_dir = os.path.dirname(os.path.abspath(__file__))
    shared_config_path = os.path.join(current_dir, 'shared_config.py')
    spec = importlib.util.spec_from_file_location("shared_config", shared_config_path)
    shared_config = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(shared_config)
    
    DEFAULT_SUPABASE_URL = shared_config.DEFAULT_SUPABASE_URL
    DEFAULT_SUPABASE_KEY = shared_config.DEFAULT_SUPABASE_KEY
    TABLE_NAMES = shared_config.TABLE_NAMES
    STOCK_CODES = shared_config.STOCK_CODES

load_dotenv()

class Config:
    """Enhanced configuration with additional parameters"""
    
    # Hardware
    DEVICE = os.getenv("DEVICE", "cuda" if torch.cuda.is_available() else "cpu")
    BATCH_SIZE = int(os.getenv("BATCH_SIZE", 5 if DEVICE == "cuda" else 2))
    
    # Supabase - sử dụng config từ crawl folder
    SUPABASE_URL = os.getenv("SUPABASE_URL", DEFAULT_SUPABASE_URL)
    SUPABASE_KEY = os.getenv("SUPABASE_KEY", DEFAULT_SUPABASE_KEY)
    
    # Model paths - hardcode path for now 
    MODEL_PATH = r"D:\SPA_vip\model_AI\summarization_model\model_vit5"
    
    # Text processing
    MAX_INPUT_LENGTH = int(os.getenv("MAX_INPUT_LENGTH", 1024))
    MAX_TARGET_LENGTH = int(os.getenv("MAX_TARGET_LENGTH", 256))
    
    # Performance
    MAX_ARTICLES_PER_RUN = int(os.getenv("MAX_ARTICLES_PER_RUN", 0))  # 0 = unlimited

    MAX_RETRIES = 3  # Try again when you encounter an error
    RETRY_DELAY = 5  # Waiting time between testing (seconds)
    
    # Tables to process (sử dụng từ crawl config)
    # News tables
    NEWS_TABLES = TABLE_NAMES  # TABLE_NAMES đã là list
        
    @staticmethod
    def get_generation_config() -> Dict[str, Any]:
        config = {
            "max_length": Config.MAX_TARGET_LENGTH,
            "min_length": 30,
            "repetition_penalty": 1.2,
            "length_penalty": 1.0,
            "early_stopping": True,
            "no_repeat_ngram_size": 3 if Config.DEVICE == "cuda" else 2,
            "num_beams": 4 if Config.DEVICE == "cuda" else 2
        }
        return config