#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Model Download Script for SPA VIP
Downloads AI models from Hugging Face Hub

Author: SPA VIP Team
Date: August 9, 2025
"""

import os
import sys
import logging
import argparse
from pathlib import Path

# Add current directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from model_manager import get_model_manager

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """Main function for downloading models"""
    parser = argparse.ArgumentParser(
        description='🤖 SPA VIP Model Downloader',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python download_models.py --all              # Download all models
  python download_models.py --sentiment        # Download sentiment model only
  python download_models.py --check            # Check model status
  python download_models.py --all --force      # Force re-download all
        """
    )
    
    # Download options
    parser.add_argument('--all', action='store_true', help='Download all models')
    parser.add_argument('--sentiment', action='store_true', help='Download sentiment model')
    parser.add_argument('--summarization', action='store_true', help='Download summarization model')
    parser.add_argument('--timeseries', action='store_true', help='Download timeseries model')
    parser.add_argument('--industry', action='store_true', help='Download industry model')
    parser.add_argument('--check', action='store_true', help='Check model status')
    parser.add_argument('--force', action='store_true', help='Force re-download')
    
    args = parser.parse_args()
    
    # Initialize model manager
    manager = get_model_manager()
    
    try:
        if args.check:
            # Check model status
            print("\n📊 MODEL STATUS CHECK")
            print("=" * 60)
            
            status = manager.check_all_models()
            all_available = True
            
            for model_type, available in status.items():
                status_icon = "✅" if available else "❌"
                status_text = "Available" if available else "Not found"
                print(f"{status_icon} {model_type.capitalize():15} : {status_text}")
                if not available:
                    all_available = False
            
            print("-" * 60)
            if all_available:
                print("🎉 All models are available locally!")
            else:
                print("⚠️  Some models are missing. Run download command to get them.")
                print("💡 Example: python download_models.py --all")
            
        elif args.all:
            # Download all models
            print("\n🚀 DOWNLOADING ALL MODELS")
            print("=" * 60)
            manager.download_all_models(force_download=args.force)
            
        elif any([args.sentiment, args.summarization, args.timeseries, args.industry]):
            # Download specific models
            print("\n🚀 DOWNLOADING SELECTED MODELS")
            print("=" * 60)
            
            if args.sentiment:
                print("📥 Downloading sentiment model...")
                manager.download_model('sentiment', force_download=args.force)
                
            if args.summarization:
                print("📥 Downloading summarization model...")
                manager.download_model('summarization', force_download=args.force)
                
            if args.timeseries:
                print("📥 Downloading timeseries model...")
                manager.download_model('timeseries', force_download=args.force)
                
            if args.industry:
                print("📥 Downloading industry model...")
                manager.download_model('industry', force_download=args.force)
            
            print("✅ Selected models downloaded successfully!")
            
        else:
            # Default: Show usage and status
            print("\n🤖 SPA VIP MODEL DOWNLOADER")
            print("=" * 60)
            print("📊 Current Model Status:")
            
            status = manager.check_all_models()
            for model_type, available in status.items():
                status_icon = "✅" if available else "❌"
                status_text = "Available" if available else "Missing"
                print(f"   {status_icon} {model_type.capitalize():15} : {status_text}")
            
            print("\n📝 AVAILABLE COMMANDS:")
            print("  python download_models.py --all           : Download all models")
            print("  python download_models.py --sentiment     : Download sentiment model")
            print("  python download_models.py --summarization : Download summarization model")
            print("  python download_models.py --timeseries    : Download timeseries model")
            print("  python download_models.py --industry      : Download industry model")
            print("  python download_models.py --check         : Check model status")
            print("  python download_models.py --all --force   : Force re-download all")
            print("=" * 60)
    
    except KeyboardInterrupt:
        logger.info("\n⚠️ Download interrupted by user")
    except Exception as e:
        logger.error(f"💥 Download failed: {str(e)}")
        raise

if __name__ == "__main__":
    main()