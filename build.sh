#!/bin/bash
# ============================================================================
# RENDER BUILD SCRIPT
# Automated build process for Render deployment
# ============================================================================

echo "🚀 Starting SPA VIP build process..."

# Upgrade pip
echo "📦 Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p logs
mkdir -p model_AI/summarization_model/model_vit5
mkdir -p model_AI/sentiment_model
mkdir -p model_AI/timeseries_model/model_lstm
mkdir -p model_AI/industry_model

# Set permissions
echo "🔐 Setting permissions..."
chmod +x main.py

echo "✅ Build completed successfully!"
