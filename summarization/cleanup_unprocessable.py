"""
Script để mark những bài không thể xử lý (content quá ngắn) với summary đặc biệt
"""
import sys
import os

# Add parent path for centralized database import
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import SupabaseManager, DatabaseConfig
from utils.logger import logger

def cleanup_unprocessable_articles():
    """Mark articles with insufficient content as unprocessable"""
    db = SupabaseManager()
    config = DatabaseConfig()
    
    # Define minimum content length
    MIN_CONTENT_LENGTH = 50
    
    # Use centralized table names
    tables = config.get_all_news_tables()
    total_marked = 0
    
    for table_name in tables:
        logger.info(f"Checking {table_name} for unprocessable articles...")
        
        # Get articles with NULL ai_summary using centralized database manager
        client = db.get_client()
        articles = client.table(table_name).select('id, title, content, ai_summary').or_('ai_summary.is.null,ai_summary.eq.').execute()
        
        marked_count = 0
        for article in articles.data:
            content_length = len(article['content']) if article['content'] else 0
            
            # If content is too short, mark as unprocessable
            if content_length < MIN_CONTENT_LENGTH:
                logger.info(f"Marking article ID {article['id']} as unprocessable (content length: {content_length})")
                
                # Update with a special marker using centralized database manager
                client.table(table_name).update({
                    'ai_summary': '[UNPROCESSABLE: Insufficient content]'
                }).eq('id', article['id']).execute()
                
                marked_count += 1
        
        logger.info(f"{table_name}: Marked {marked_count} articles as unprocessable")
        total_marked += marked_count
    
    logger.info(f"Total articles marked as unprocessable: {total_marked}")
    return total_marked

if __name__ == "__main__":
    cleanup_unprocessable_articles()
