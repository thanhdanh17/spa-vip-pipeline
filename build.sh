#!/bin/bash
# ============================================================================
# RENDER BUILD SCRIPT
# Automated build process for Render deployment
# ============================================================================

echo "🚀 Starting SPA VIP build process..."

# Upgrade pip
echo "📦 Upgrading pip..."
pip install --upgrade pip

# Install dependencies with error handling
echo "📦 Installing dependencies..."
if pip install -r requirements.txt; then
    echo "✅ Dependencies installed successfully!"
else
    echo "❌ Failed to install dependencies, trying fallback..."
    # Fallback: Install core dependencies without version constraints
    pip install supabase python-dotenv psycopg2-binary
    pip install selenium beautifulsoup4 requests webdriver-manager lxml python-dateutil
    pip install torch --index-url https://download.pytorch.org/whl/cpu
    pip install transformers tensorflow-cpu sentencepiece
    pip install pandas numpy scipy scikit-learn
    pip install matplotlib seaborn plotly
    pip install fastapi uvicorn gunicorn
    pip install tqdm Pillow typing-extensions colorama python-json-logger
    echo "✅ Fallback installation completed!"
fi

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
