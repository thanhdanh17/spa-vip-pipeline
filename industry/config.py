import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
BASE_DIR = Path(__file__).parent

# Add parent directory to path for centralized database import
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

# Import centralized database system
from database import DatabaseConfig

class Config:
    # Use centralized database config
    DATABASE_CONFIG = DatabaseConfig()
    
    # Model paths - Updated to use model_AI centralized structure
    MODEL_INDUSTRY_PATH = os.path.join(parent_dir, 'model_AI', 'industry_model', 'PhoBERT_summary_industry.bin')
    
    # Table configuration - Industry classification only works on General_News
    NEWS_TABLES = ['General_News']  # Only process general news for industry classification
    
    # Column names standardized with SPA VIP schema
    TITLE_COLUMN = 'title'
    CONTENT_COLUMN = 'content'
    DATETIME_COLUMN = 'date'
    SUMMARY_COLUMN = 'ai_summary'
    INDUSTRY_COLUMN = 'industry'
    
    # Industry classification labels (matching trained model - 5 classes)
    INDUSTRY_LABELS = [
        'Finance',      # Tài chính - Ngân hàng
        'Technology',   # Công nghệ
        'Healthcare',   # Y tế - Dược phẩm
        'Energy',       # Năng lượng - Dầu khí
        'Other'         # Khác
    ]
    
    # Processing configuration
    BATCH_SIZE = 50
    PROCESSING_INTERVAL = 60  # seconds