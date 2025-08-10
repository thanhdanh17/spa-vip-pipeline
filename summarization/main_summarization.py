import time
import sys
import os
import importlib.util
from typing import List, Dict
from tqdm import tqdm

# Import centralized database system
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import SupabaseManager, DatabaseConfig

# Wrapper class for backward compatibility
class SupabaseHandler:
    def __init__(self):
        self.db_manager = SupabaseManager()
        self.config = DatabaseConfig()
    
    def fetch_unsummarized_articles(self, limit=100, table_name=None):
        return self.db_manager.fetch_unsummarized_articles(table_name, limit)
    
    def update_summary(self, article_id, summary, table_name):
        return self.db_manager.update_article_summary(article_id, summary, table_name)
    
    def get_table_stats(self):
        return self.db_manager.get_table_stats()

from .models.summarizer import NewsSummarizer

# Import Config bằng cách explicit để tránh conflict
current_dir = os.path.dirname(os.path.abspath(__file__))
config_file = os.path.join(current_dir, 'config.py')
spec = importlib.util.spec_from_file_location("summarization_config", config_file)
config_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(config_module)
Config = config_module.Config

from utils.logger import logger
from utils.helpers import measure_performance

# Import table names from centralized config
TABLE_NAMES = DatabaseConfig().get_all_news_tables()

class SummarizationPipeline:
    """Enhanced pipeline for batch processing news from crawl database"""
    
    def __init__(self):
        self.db = SupabaseHandler()
        self.summarizer = None  # Lazy loading để tiết kiệm memory
        self.start_time = None
        self.processed_count = 0
        self.error_count = 0
        
        logger.info("Enhanced Summarization Pipeline initialized")
        
        # Log table statistics
        self.log_table_stats()
    
    def _load_model(self):
        """Lazy load model để tiết kiệm memory"""
        if self.summarizer is None:
            logger.info("Loading AI model...")
            # Use ModelManager instead of direct NewsSummarizer
            try:
                from models.model_manager import get_model_manager
                manager = get_model_manager()
                self.summarizer = manager.load_summarization_model()
                logger.info("✅ Model loaded via ModelManager")
            except Exception as e:
                logger.error(f"❌ Failed to load model via ModelManager: {e}")
                # Fallback to direct NewsSummarizer if needed
                self.summarizer = NewsSummarizer()
                logger.info("Model loaded via fallback")
    
    def log_table_stats(self):
        """Log statistics for all news tables với priority analysis"""
        logger.info("DATABASE STATISTICS")
        logger.info("=" * 50)
        
        stats = self.db.get_table_stats()
        total_articles = 0
        total_unsummarized = 0
        
        # Tính toán priority cho các bảng
        table_priorities = []
        
        for table_name, table_stats in stats.items():
            completion_rate = (table_stats['summarized'] / table_stats['total'] * 100) if table_stats['total'] > 0 else 100
            priority_score = table_stats['unsummarized'] * (100 - completion_rate)
            
            table_priorities.append({
                'name': table_name,
                'stats': table_stats,
                'completion_rate': completion_rate,
                'priority_score': priority_score
            })
            
            total_articles += table_stats['total']
            total_unsummarized += table_stats['unsummarized']
        
        # Sort theo priority (completion rate thấp nhất trước)
        table_priorities.sort(key=lambda x: x['completion_rate'])
        
        # Log theo thứ tự priority
        for i, table_info in enumerate(table_priorities, 1):
            table_name = table_info['name']
            table_stats = table_info['stats']
            completion_rate = table_info['completion_rate']
            
            # Updated estimate: 11 giây/bài (based on performance testing)
            estimated_minutes = table_stats['unsummarized'] * 11 / 60
            
            status = "DONE" if table_stats['unsummarized'] == 0 else f"{table_stats['unsummarized']} pending"
            
            logger.info(f"{i}. {table_name}: {table_stats['summarized']}/{table_stats['total']} ({completion_rate:.1f}%) | {status}")
            if table_stats['unsummarized'] > 0:
                logger.info(f"   ETA: {estimated_minutes:.1f}min")
        
        logger.info("=" * 50)
        if total_articles > 0:
            completion_pct = ((total_articles - total_unsummarized)/total_articles*100)
            logger.info(f"OVERALL: {total_articles - total_unsummarized}/{total_articles} articles completed ({completion_pct:.1f}%)")
        else:
            logger.info("OVERALL: No articles found in database")
        logger.info(f"REMAINING: {total_unsummarized} articles | Total ETA: {total_unsummarized * 11 / 60:.1f} minutes")
        logger.info("=" * 50)
    
    @measure_performance
    def process_batch(self, batch_size: int = 20, table_name: str = None) -> int:
        """Process a batch of articles with improved logging"""
        total_success = 0
        while True:
            articles = self.db.fetch_unsummarized_articles(limit=batch_size, table_name=table_name)
            if not articles:
                if total_success == 0:
                    logger.info(f"No articles to process in {table_name or 'all tables'}")
                break
            
            logger.info(f"Processing {len(articles)} articles from {table_name or 'multiple tables'}")
            contents = [article["content"] for article in articles]
            
            try:
                summaries = self.summarizer.summarize_batch(contents)
                success_count = 0
                
                for article, summary in zip(articles, summaries):
                    if summary and self.db.update_summary(
                        article["id"], 
                        summary, 
                        article["table_name"]
                    ):
                        success_count += 1
                        
                logger.info(f"Successfully processed {success_count}/{len(articles)} articles")
                total_success += success_count
                
            except Exception as e:
                logger.error(f"Batch processing failed: {str(e)}")
                break
                
        return total_success

    def process_all_articles(self):
        """Process ALL unsummarized articles until completion"""
        total_processed = 0
        batch_size = Config.BATCH_SIZE
        
        # Get list of news tables
        news_tables = Config.NEWS_TABLES
        
        logger.info(f"Processing articles from tables: {news_tables}")
        
        with tqdm(desc="Processing ALL articles") as pbar:
            while True:
                articles = self.db.fetch_unsummarized_articles(limit=batch_size)
                if not articles:
                    break
                    
                contents = [article["content"] for article in articles]
                summaries = self.summarizer.summarize_batch(contents)
                
                batch_processed = 0
                for article, summary in zip(articles, summaries):
                    if summary and self.db.update_summary(
                        article["id"], 
                        summary, 
                        article["table_name"]
                    ):
                        batch_processed += 1
                
                total_processed += batch_processed
                pbar.update(batch_processed)
                pbar.set_postfix({"Processed": total_processed})
                
                if Config.DEVICE == "cpu":
                    time.sleep(1)
        
        logger.info(f"FINISHED! Total articles processed: {total_processed}")
        return total_processed

    def process_specific_table(self, table_name: str):
        """Process articles from a specific table with enhanced progress tracking"""
        logger.info(f"Processing specific table: {table_name}")
        
        # Load model trước khi bắt đầu
        self._load_model()
        
        # Get initial stats
        initial_stats = self.db.get_table_stats().get(table_name, {})
        total_to_process = initial_stats.get('unsummarized', 0)
        
        if total_to_process == 0:
            logger.info(f"{table_name} is already 100% complete!")
            return 0
        
        total_processed = 0
        batch_size = Config.BATCH_SIZE
        batch_count = 0
        
        logger.info(f"Configuration: Batch size {batch_size} | Device: {Config.DEVICE}")
        logger.info(f"Target: {total_to_process} articles | ETA: {total_to_process * 11 / 60:.1f} minutes")
        logger.info("Starting processing...")
        logger.info("=" * 60)
        
        start_time = time.time()
        
        with tqdm(total=total_to_process, desc=f"Processing {table_name}", 
                 bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}]") as pbar:
            
            while True:
                articles = self.db.fetch_unsummarized_articles(limit=batch_size, table_name=table_name)
                if not articles:
                    logger.info(f"✅ No more articles to process in {table_name}")
                    break
                
                batch_count += 1
                batch_start = time.time()
                
                # Clear và informative batch logging
                logger.info(f"\n� BATCH {batch_count} | Processing {len(articles)} articles...")
                
                contents = [article["content"] for article in articles]
                
                try:
                    # AI processing
                    logger.info("AI summarizing...")
                    summaries = self.summarizer.summarize_batch(contents)
                    
                    # Database updates
                    logger.info("Saving to database...")
                    batch_processed = 0
                    for article, summary in zip(articles, summaries):
                        if summary and self.db.update_summary(
                            article["id"], 
                            summary, 
                            article["table_name"]
                        ):
                            batch_processed += 1
                    
                    # Update counters
                    total_processed += batch_processed
                    pbar.update(batch_processed)
                    
                    # Batch completion
                    batch_time = time.time() - batch_start
                    avg_time = batch_time / len(articles)
                    
                    logger.info(f"BATCH {batch_count} COMPLETE: {batch_processed}/{len(articles)} articles | {batch_time:.1f}s | {avg_time:.1f}s/article")
                    
                    # Progress summary
                    completion_rate = (total_processed / total_to_process) * 100
                    remaining = total_to_process - total_processed
                    estimated_remaining_time = remaining * avg_time / 60
                    
                    logger.info(f"PROGRESS: {total_processed}/{total_to_process} ({completion_rate:.1f}%) | ETA: {estimated_remaining_time:.1f}min")
                    logger.info("-" * 60)
                    
                    if Config.DEVICE == "cpu":
                        time.sleep(1)  # Brief pause cho CPU
                
                except Exception as e:
                    logger.error(f"BATCH {batch_count} ERROR: {str(e)}")
                    logger.info("Continuing to next batch...")
                    continue
        
        # Final summary
        total_time = time.time() - start_time
        avg_speed = total_processed / total_time if total_time > 0 else 0
        success_rate = (total_processed / total_to_process) * 100 if total_to_process > 0 else 0
        
        logger.info("=" * 60)
        logger.info(f"{table_name} PROCESSING COMPLETED!")
        logger.info(f"RESULTS:")
        logger.info(f"   Articles processed: {total_processed}/{total_to_process}")
        logger.info(f"   Total time: {total_time/60:.1f} minutes")
        logger.info(f"   Speed: {avg_speed:.2f} articles/second")
        logger.info(f"   Success rate: {success_rate:.1f}%")
        logger.info("=" * 60)
        
        return total_processed

    def process_all_tables_by_priority(self):
        """Process all tables theo thứ tự priority với enhanced tracking"""
        try:
            logger.info("🎯 Starting priority-based processing pipeline...")
            
            # Get table statistics và tính priority
            stats = self.db.get_table_stats()
            table_priorities = []
            
            for table_name, table_stats in stats.items():
                if table_stats['unsummarized'] > 0:
                    completion_rate = (table_stats['summarized'] / table_stats['total'] * 100) if table_stats['total'] > 0 else 100
                    priority_score = table_stats['unsummarized'] * (100 - completion_rate)
                    
                    table_priorities.append({
                        'name': table_name,
                        'unsummarized': table_stats['unsummarized'],
                        'total': table_stats['total'],
                        'completion_rate': completion_rate,
                        'priority_score': priority_score
                    })
            
            # Sort theo priority (completion rate thấp nhất trước - cần attention nhất)
            table_priorities.sort(key=lambda x: x['completion_rate'])
            
            if not table_priorities:
                logger.info("✅ All tables are already fully processed!")
                return
            
            total_articles_to_process = sum(t['unsummarized'] for t in table_priorities)
            total_eta_minutes = total_articles_to_process * 11 / 60  # Improved estimate
            
            logger.info("�" * 20)
            logger.info(f"📋 PRIORITY PROCESSING QUEUE: {len(table_priorities)} tables")
            logger.info(f"📊 Total articles to process: {total_articles_to_process}")
            logger.info(f"⏱️ Estimated total time: {total_eta_minutes:.1f} minutes")
            logger.info("🔥" * 20)
            
            for i, table_info in enumerate(table_priorities, 1):
                eta_minutes = table_info['unsummarized'] * 11 / 60
                logger.info(f"{i}. 🎯 {table_info['name']}: {table_info['unsummarized']}/{table_info['total']} articles ({table_info['completion_rate']:.1f}% done) - ETA: {eta_minutes:.1f}min")
            
            logger.info("🔥" * 20)
            
            # Process từng table theo priority
            overall_start = time.time()
            total_processed_all = 0
            
            for i, table_info in enumerate(table_priorities, 1):
                table_name = table_info['name']
                
                logger.info(f"\n🚀 TABLE {i}/{len(table_priorities)}: {table_name}")
                logger.info(f"📊 Queue status: {table_info['unsummarized']} articles remaining")
                logger.info("🔄 Starting processing...")
                
                table_start = time.time()
                processed = self.process_specific_table(table_name)
                table_time = time.time() - table_start
                
                total_processed_all += processed
                
                logger.info(f"✅ TABLE {i} COMPLETED: {table_name}")
                logger.info(f"   📈 Processed: {processed} articles in {table_time/60:.1f} minutes")
                
                # Overall progress
                remaining_tables = len(table_priorities) - i
                overall_progress = (i / len(table_priorities)) * 100
                
                if remaining_tables > 0:
                    logger.info(f"🎯 OVERALL PROGRESS: {overall_progress:.1f}% | {remaining_tables} tables remaining")
                    logger.info("🔄 Moving to next priority table...\n")
            
            # Final pipeline summary
            total_time = time.time() - overall_start
            logger.info("=" * 50)
            logger.info("PRIORITY PIPELINE COMPLETED!")
            logger.info(f"FINAL RESULTS:")
            logger.info(f"   Total articles processed: {total_processed_all}")
            logger.info(f"   Total pipeline time: {total_time/60:.1f} minutes")
            logger.info(f"   Overall speed: {total_processed_all/(total_time/60):.1f} articles/minute")
            logger.info(f"   Tables completed: {len(table_priorities)}")
            logger.info("=" * 50)
            
        except Exception as e:
            logger.error(f"Error in priority processing: {str(e)}")
            raise

def main_summarization():
    """Main function với standardized pipeline options"""
    import argparse
    
    parser = argparse.ArgumentParser(description='📰 Vietnamese News Summarization Pipeline')
    parser.add_argument('--table', '-t', help='Process specific table only', 
                       choices=['General_News', 'FPT_News', 'GAS_News', 'IMP_News', 'VCB_News'])
    parser.add_argument('--stats', '-s', action='store_true', help='Show database statistics only')
    parser.add_argument('--priority', '-p', action='store_true', help='Process all tables by priority (RECOMMENDED)')
    parser.add_argument('--all', '-a', action='store_true', help='Process all tables sequentially')
    
    args = parser.parse_args()
    
    # Initialize pipeline
    pipeline = SummarizationPipeline()
    
    try:
        if args.stats:
            # Show statistics only
            return
            
        if args.table:
            # Process specific table
            logger.info(f"🎯 Processing specific table: {args.table}")
            pipeline.process_specific_table(args.table)
            
        elif args.priority:
            # Process by priority (RECOMMENDED)
            pipeline.process_all_tables_by_priority()
            
        elif args.all:
            # Process all tables sequentially
            logger.info("🔄 Processing all tables sequentially...")
            pipeline.process_all_articles()
            
        else:
            # Default: Show usage và stats
            print("\n" + "="*60)
            print("� VIETNAMESE NEWS SUMMARIZATION PIPELINE")
            print("="*60)
            print("�📊 Current Status:")
            pipeline.log_table_stats()
            print("\n" + "-"*60)
            print("� AVAILABLE COMMANDS:")
            print("  python main.py --priority     : Process all tables by priority (RECOMMENDED)")
            print("  python main.py --table [name] : Process specific table only")
            print("  python main.py --all          : Process all tables sequentially")
            print("  python main.py --stats        : Show statistics only")
            print("-"*60)
            print("\n🎯 Recommended: python main.py --priority")
            print("="*60)
            
    except KeyboardInterrupt:
        logger.info("\nProcessing interrupted by user")
    except Exception as e:
        logger.error(f"Pipeline error: {str(e)}")
        raise

if __name__ == "__main__":
    main_summarization()