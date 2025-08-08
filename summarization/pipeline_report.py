"""
Simple monitoring dashboard for the summarization pipeline
"""
import sys
import os
from datetime import datetime

# Add crawl path
crawl_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'crawl')
if crawl_path not in sys.path:
    sys.path.insert(0, crawl_path)

from database.supabase_handler import SupabaseHandler

def generate_report():
    """Generate comprehensive pipeline report"""
    db = SupabaseHandler()
    
    print("=" * 80)
    print("🗞️  VIETNAMESE NEWS SUMMARIZATION PIPELINE REPORT")
    print("=" * 80)
    print(f"📅 Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Get statistics
    stats = db.get_table_stats()
    
    # Calculate totals
    total_articles = sum(table_stats['total'] for table_stats in stats.values())
    total_summarized = sum(table_stats['summarized'] for table_stats in stats.values())
    total_pending = sum(table_stats['unsummarized'] for table_stats in stats.values())
    
    overall_completion = (total_summarized / total_articles * 100) if total_articles > 0 else 0
    
    print("📊 OVERALL STATISTICS")
    print("-" * 40)
    print(f"Total Articles: {total_articles:,}")
    print(f"Summarized: {total_summarized:,}")
    print(f"Pending: {total_pending:,}")
    print(f"Completion Rate: {overall_completion:.2f}%")
    print()
    
    print("📋 TABLE BREAKDOWN")
    print("-" * 40)
    print(f"{'Table':<15} {'Total':<8} {'Done':<8} {'Pending':<8} {'Rate':<8}")
    print("-" * 50)
    
    for table_name, table_stats in stats.items():
        completion_rate = (table_stats['summarized'] / table_stats['total'] * 100) if table_stats['total'] > 0 else 100
        print(f"{table_name:<15} {table_stats['total']:<8} {table_stats['summarized']:<8} {table_stats['unsummarized']:<8} {completion_rate:.1f}%")
    
    print()
    print("🎯 RECOMMENDATIONS")
    print("-" * 40)
    
    if total_pending == 0:
        print("✅ All processable articles have been summarized!")
        print("🚀 Pipeline is ready for production use")
    elif total_pending <= 5:
        print(f"⚠️  Only {total_pending} articles pending - likely unprocessable content")
        print("💡 Consider running cleanup script to mark them as unprocessable")
    else:
        print(f"🔄 {total_pending} articles pending processing")
        print("💡 Run: python main_summarization.py --priority")
    
    print()
    print("🔧 NEXT STEPS")
    print("-" * 40)
    print("1. Set up automated crawling schedule")
    print("2. Create API endpoints for serving summaries")
    print("3. Implement real-time monitoring")
    print("4. Add more news sources")
    print("=" * 80)

if __name__ == "__main__":
    generate_report()
