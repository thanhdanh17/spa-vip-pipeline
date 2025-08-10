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

# Install PyTorch first with CPU-only index
echo "🔥 Installing PyTorch (CPU-only)..."
pip install torch --index-url https://download.pytorch.org/whl/cpu

# Install TensorFlow CPU
echo "🧠 Installing TensorFlow (CPU-only)..."
pip install tensorflow

# Install remaining dependencies
echo "📦 Installing remaining dependencies..."
if pip install -r requirements.txt; then
    echo "✅ All dependencies installed successfully!"
else
    echo "❌ Some dependencies failed, trying fallback..."
    # Fallback: Install core dependencies individually
    pip install supabase python-dotenv psycopg2-binary
    pip install selenium beautifulsoup4 requests webdriver-manager lxml python-dateutil
    pip install transformers sentencepiece accelerate huggingface-hub
    pip install pandas numpy scipy scikit-learn
    pip install matplotlib seaborn plotly
    pip install fastapi uvicorn gunicorn python-multipart httpx aiofiles
    pip install pydantic python-jose structlog
    pip install tqdm Pillow typing-extensions colorama python-json-logger
    echo "✅ Fallback installation completed!"
fi

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p logs
mkdir -p model_cache

# Download AI models from Hugging Face
echo "🤖 Downloading AI models from Hugging Face..."
if python models/download_models.py --all; then
    echo "✅ All models downloaded successfully!"
else
    echo "⚠️ Model download failed, will fallback to runtime download"
fi

# Set permissions
echo "🔐 Setting permissions..."
chmod +x main.py

echo "✅ Build completed successfully!"
