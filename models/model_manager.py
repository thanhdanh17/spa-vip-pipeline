#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Model Manager for Hugging Face Integration
Manages downloading and loading models from Hugging Face Hub

Author: SPA VIP Team
Date: August 9, 2025
"""

import os
import logging
from pathlib import Path
from typing import Optional, Dict, Any
import torch
from transformers import AutoTokenizer, AutoModel, T5ForConditionalGeneration, T5Tokenizer
from huggingface_hub import hf_hub_download, snapshot_download
import tensorflow as tf

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ModelManager:
    """
    Centralized model manager for Hugging Face integration
    """
    
    # Model configurations on Hugging Face
    MODEL_CONFIGS = {
        'sentiment': {
            'repo_id': 'danhne123/sentiment_model',
            'model_file': 'Phobert_hyper_parameters/PhoBERT_summary_sentiment_optuna.bin',
            'base_model': 'vinai/phobert-base',
            'local_dir': 'model_AI/sentiment_model/Phobert_hyper_parameters'
        },
        'summarization': {
            'repo_id': 'danhne123/summary_model',
            'subfolder': 'model_vit5',
            'local_dir': 'model_AI/summarization_model/model_vit5'
        },
        'timeseries': {
            'repo_id': 'danhne123/timeseries',
            'model_file': 'model_lstm/LSTM_missing10_window15.keras',
            'local_dir': 'model_AI/timeseries_model/model_lstm'
        },
        'industry': {
            'repo_id': 'danhne123/industry_model',
            'model_file': 'PhoBERT_summary_industry.bin',
            'base_model': 'vinai/phobert-base',
            'local_dir': 'model_AI/industry_model'
        }
    }
    
    def __init__(self, cache_dir: Optional[str] = None):
        """
        Initialize ModelManager - HuggingFace only mode
        
        Args:
            cache_dir: Local cache directory for downloaded models (default: ./model_cache)
        """
        self.cache_dir = Path(cache_dir) if cache_dir else Path('./model_cache')
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Track loaded models
        self._loaded_models = {}
        
        logger.info(f"ModelManager initialized with cache_dir: {self.cache_dir} (HuggingFace only)")
    
    def download_model(self, model_type: str, force_download: bool = False) -> str:
        """
        Download model from Hugging Face Hub
        
        Args:
            model_type: Type of model ('sentiment', 'summarization', 'timeseries', 'industry')
            force_download: Force re-download even if model exists locally
            
        Returns:
            str: Local path to downloaded model
        """
        if model_type not in self.MODEL_CONFIGS:
            raise ValueError(f"Unknown model type: {model_type}")
        
        config = self.MODEL_CONFIGS[model_type]
        local_dir = self.cache_dir / config['local_dir'].replace('model_AI/', '')
        
        # Always download from HuggingFace
        try:
            logger.info(f"Downloading {model_type} model from {config['repo_id']}...")
            
            # Create local directory
            local_dir.mkdir(parents=True, exist_ok=True)
            
            if 'model_file' in config:
                # Download specific model file
                downloaded_path = hf_hub_download(
                    repo_id=config['repo_id'],
                    filename=config['model_file'],
                    local_dir=str(local_dir),
                    local_dir_use_symlinks=False
                )
                logger.info(f"Downloaded model file: {downloaded_path}")
            elif 'subfolder' in config:
                # Download specific subfolder
                downloaded_path = snapshot_download(
                    repo_id=config['repo_id'],
                    allow_patterns=f"{config['subfolder']}/*",
                    local_dir=str(local_dir.parent),
                    local_dir_use_symlinks=False
                )
                logger.info(f"Downloaded subfolder: {downloaded_path}")
            else:
                # Download entire repository
                downloaded_path = snapshot_download(
                    repo_id=config['repo_id'],
                    local_dir=str(local_dir),
                    local_dir_use_symlinks=False
                )
                logger.info(f"Downloaded model repository: {downloaded_path}")
            
            return str(local_dir)
            
        except Exception as e:
            logger.error(f"Failed to download {model_type} model: {str(e)}")
            raise
    
    def _model_exists_locally(self, model_type: str) -> bool:
        """Check if model exists locally"""
        config = self.MODEL_CONFIGS[model_type]
        local_dir = self.cache_dir / config['local_dir'].replace('model_AI/', '')
        
        if 'model_file' in config:
            # Check for specific model file
            model_path = local_dir / config['model_file']
            return model_path.exists()
        else:
            # Check for directory with expected files
            required_files = ['config.json']  # Basic check
            if model_type == 'summarization':
                required_files.extend(['model.safetensors', 'tokenizer_config.json'])
            
            return all((local_dir / file).exists() for file in required_files)
    
    def get_model_path(self, model_type: str) -> str:
        """
        Get local path for model, download from HuggingFace if necessary
        
        Args:
            model_type: Type of model
            
        Returns:
            str: Local path to model
        """
        # Always ensure model is available from HuggingFace
        if not self._model_exists_locally(model_type):
            logger.info(f"Downloading {model_type} model from HuggingFace...")
            return self.download_model(model_type)
        
        config = self.MODEL_CONFIGS[model_type]
        local_dir = self.cache_dir / config['local_dir'].replace('model_AI/', '')
        logger.info(f"Using cached {model_type} model from: {local_dir}")
        return str(local_dir)
    
    def load_sentiment_model(self):
        """Load sentiment analysis model"""
        from sentiment.predict_sentiment_db import SentimentClassifier
        
        try:
            model_path = self.get_model_path('sentiment')
            config = self.MODEL_CONFIGS['sentiment']
            
            # Load model
            model = SentimentClassifier(n_classes=3)
            model_file_path = os.path.join(model_path, config['model_file'])
            model.load_state_dict(torch.load(model_file_path, map_location="cpu"))
            model.eval()
            
            # Load tokenizer
            tokenizer = AutoTokenizer.from_pretrained(config['base_model'])
            id2label = {0: "Positive", 1: "Negative", 2: "Neutral"}
            
            logger.info("✅ Sentiment model loaded successfully")
            return model, tokenizer, id2label
            
        except Exception as e:
            logger.error(f"❌ Failed to load sentiment model: {str(e)}")
            raise
    
    def load_summarization_model(self):
        """Load summarization model"""
        try:
            model_path = self.get_model_path('summarization')
            
            # Load tokenizer and model
            tokenizer = T5Tokenizer.from_pretrained(
                model_path,
                legacy=False,
                local_files_only=True
            )
            
            model = T5ForConditionalGeneration.from_pretrained(
                model_path,
                local_files_only=True
            )
            
            logger.info("✅ Summarization model loaded successfully")
            return model, tokenizer
            
        except Exception as e:
            logger.error(f"❌ Failed to load summarization model: {str(e)}")
            raise
    
    def load_timeseries_model(self):
        """Load timeseries prediction model"""
        try:
            model_path = self.get_model_path('timeseries')
            config = self.MODEL_CONFIGS['timeseries']
            
            model_file_path = os.path.join(model_path, config['model_file'])
            model = tf.keras.models.load_model(model_file_path)
            
            logger.info("✅ Timeseries model loaded successfully")
            return model
            
        except Exception as e:
            logger.error(f"❌ Failed to load timeseries model: {str(e)}")
            raise
    
    def load_industry_model(self):
        """Load industry classification model"""
        from industry.models.phobert_classifier import IndustryClassifier
        
        try:
            model_path = self.get_model_path('industry')
            config = self.MODEL_CONFIGS['industry']
            
            # Load model
            labels = ["Tài chính - Ngân hàng", "Công nghệ", "Năng lượng", "Sản xuất", "Khác"]
            model = IndustryClassifier(n_classes=len(labels))
            
            model_file_path = os.path.join(model_path, config['model_file'])
            model.load_state_dict(torch.load(model_file_path, map_location="cpu"))
            model.eval()
            
            # Load tokenizer
            tokenizer = AutoTokenizer.from_pretrained(config['base_model'])
            
            logger.info("✅ Industry model loaded successfully")
            return model, tokenizer, labels
            
        except Exception as e:
            logger.error(f"❌ Failed to load industry model: {str(e)}")
            raise
    
    def download_all_models(self, force_download: bool = False):
        """Download all models"""
        logger.info("🚀 Starting download of all models...")
        
        for model_type in self.MODEL_CONFIGS.keys():
            try:
                self.download_model(model_type, force_download)
                logger.info(f"✅ {model_type} model downloaded successfully")
            except Exception as e:
                logger.error(f"❌ Failed to download {model_type} model: {str(e)}")
        
        logger.info("🎉 All model downloads completed!")
    
    def check_all_models(self) -> Dict[str, bool]:
        """Check if all models are available locally"""
        status = {}
        for model_type in self.MODEL_CONFIGS.keys():
            status[model_type] = self._model_exists_locally(model_type)
        return status
    
    def update_model_configs(self, new_configs: Dict[str, Dict[str, Any]]):
        """Update model configurations with actual Hugging Face repo URLs"""
        for model_type, config in new_configs.items():
            if model_type in self.MODEL_CONFIGS:
                self.MODEL_CONFIGS[model_type].update(config)
        
        logger.info("✅ Model configurations updated")


# Global model manager instance
model_manager = ModelManager()

def get_model_manager() -> ModelManager:
    """Get global model manager instance"""
    return model_manager


if __name__ == "__main__":
    """Test script for model manager"""
    import argparse
    
    parser = argparse.ArgumentParser(description='SPA VIP Model Manager')
    parser.add_argument('--download-all', action='store_true', help='Download all models')
    parser.add_argument('--check', action='store_true', help='Check model status')
    parser.add_argument('--force', action='store_true', help='Force re-download')
    
    args = parser.parse_args()
    
    manager = get_model_manager()
    
    if args.check:
        print("\n📊 MODEL STATUS:")
        print("=" * 50)
        status = manager.check_all_models()
        for model_type, available in status.items():
            status_icon = "✅" if available else "❌"
            print(f"{status_icon} {model_type}: {'Available' if available else 'Not found'}")
    
    if args.download_all:
        print("\n🚀 DOWNLOADING ALL MODELS:")
        print("=" * 50)
        manager.download_all_models(force_download=args.force)
    
    if not args.check and not args.download_all:
        print("\n🤖 SPA VIP Model Manager")
        print("=" * 50)
        print("Usage:")
        print("  python model_manager.py --check        # Check model status")
        print("  python model_manager.py --download-all # Download all models")
        print("  python model_manager.py --download-all --force # Force re-download")
