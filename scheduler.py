#!/usr/bin/env python3
"""
SPA VIP - Automated Scheduler
Runs pipeline jobs on schedule for continuous operation
"""

import schedule
import time
import subprocess
import logging
from datetime import datetime
import requests
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SPAScheduler:
    def __init__(self, base_url=None):
        """Initialize scheduler with base URL for API calls"""
        self.base_url = base_url or "http://localhost:8000"
        self.setup_schedule()
    
    def setup_schedule(self):
        """Setup the job schedule"""
        # Crawl every hour
        schedule.every(1).hours.do(self.run_crawl_job)
        
        # Sentiment analysis every 4 hours
        schedule.every(4).hours.do(self.run_sentiment_job)
        
        # Full pipeline daily at 2 AM
        schedule.every().day.at("02:00").do(self.run_full_pipeline_job)
        
        # Health check every 30 minutes
        schedule.every(30).minutes.do(self.health_check)
        
        logger.info("📅 Schedule configured:")
        logger.info("  🕷️  Crawl: Every 1 hour")
        logger.info("  💭 Sentiment: Every 4 hours")
        logger.info("  🔄 Full Pipeline: Daily at 2:00 AM")
        logger.info("  ❤️  Health Check: Every 30 minutes")
    
    def run_crawl_job(self):
        """Execute crawl job"""
        logger.info("🕷️ Starting scheduled crawl job...")
        try:
            # Option 1: Call API endpoint
            response = requests.post(f"{self.base_url}/pipeline/crawl", timeout=60)
            if response.status_code == 200:
                logger.info("✅ Crawl job triggered successfully via API")
            else:
                logger.error(f"❌ API call failed: {response.status_code}")
                # Fallback to direct execution
                self._run_direct_crawl()
        except Exception as e:
            logger.error(f"❌ API call failed: {e}")
            # Fallback to direct execution
            self._run_direct_crawl()
    
    def _run_direct_crawl(self):
        """Direct crawl execution as fallback"""
        try:
            result = subprocess.run(
                ["python", "main.py", "--crawl-only"],
                capture_output=True,
                text=True,
                timeout=1800  # 30 minutes
            )
            if result.returncode == 0:
                logger.info("✅ Direct crawl completed successfully")
            else:
                logger.error(f"❌ Direct crawl failed: {result.stderr}")
        except Exception as e:
            logger.error(f"❌ Direct crawl execution failed: {e}")
    
    def run_sentiment_job(self):
        """Execute sentiment analysis job"""
        logger.info("💭 Starting scheduled sentiment analysis...")
        try:
            response = requests.post(f"{self.base_url}/pipeline/sentiment", timeout=60)
            if response.status_code == 200:
                logger.info("✅ Sentiment job triggered successfully")
            else:
                logger.error(f"❌ Sentiment API call failed: {response.status_code}")
                self._run_direct_sentiment()
        except Exception as e:
            logger.error(f"❌ Sentiment API call failed: {e}")
            self._run_direct_sentiment()
    
    def _run_direct_sentiment(self):
        """Direct sentiment execution as fallback"""
        try:
            result = subprocess.run(
                ["python", "main.py", "--sentiment-only"],
                capture_output=True,
                text=True,
                timeout=600  # 10 minutes
            )
            if result.returncode == 0:
                logger.info("✅ Direct sentiment analysis completed")
            else:
                logger.error(f"❌ Direct sentiment failed: {result.stderr}")
        except Exception as e:
            logger.error(f"❌ Direct sentiment execution failed: {e}")
    
    def run_full_pipeline_job(self):
        """Execute full pipeline job"""
        logger.info("🔄 Starting scheduled full pipeline...")
        try:
            response = requests.post(f"{self.base_url}/pipeline/run", timeout=120)
            if response.status_code == 200:
                logger.info("✅ Full pipeline triggered successfully")
            else:
                logger.error(f"❌ Full pipeline API call failed: {response.status_code}")
                self._run_direct_full()
        except Exception as e:
            logger.error(f"❌ Full pipeline API call failed: {e}")
            self._run_direct_full()
    
    def _run_direct_full(self):
        """Direct full pipeline execution as fallback"""
        try:
            result = subprocess.run(
                ["python", "main.py", "--full"],
                capture_output=True,
                text=True,
                timeout=3600  # 1 hour
            )
            if result.returncode == 0:
                logger.info("✅ Direct full pipeline completed")
            else:
                logger.error(f"❌ Direct full pipeline failed: {result.stderr}")
        except Exception as e:
            logger.error(f"❌ Direct full pipeline execution failed: {e}")
    
    def health_check(self):
        """Check system health"""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=30)
            if response.status_code == 200:
                data = response.json()
                logger.info(f"❤️ Health check: {data.get('status', 'unknown')}")
            else:
                logger.warning(f"⚠️ Health check failed: {response.status_code}")
        except Exception as e:
            logger.error(f"❌ Health check failed: {e}")
    
    def run(self):
        """Start the scheduler"""
        logger.info("🚀 SPA VIP Scheduler started!")
        logger.info(f"📡 API Base URL: {self.base_url}")
        
        # Run initial health check
        self.health_check()
        
        while True:
            try:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
            except KeyboardInterrupt:
                logger.info("🛑 Scheduler stopped by user")
                break
            except Exception as e:
                logger.error(f"❌ Scheduler error: {e}")
                time.sleep(60)  # Wait before retry

def main():
    """Main entry point"""
    # Get base URL from environment or use localhost
    base_url = os.environ.get("API_BASE_URL", "http://localhost:8000")
    
    scheduler = SPAScheduler(base_url=base_url)
    scheduler.run()

if __name__ == "__main__":
    main()
