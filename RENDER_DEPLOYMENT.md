# ============================================================================
# SPA VIP - RENDER DEPLOYMENT GUIDE
# Complete guide for deploying to Render.com
# ============================================================================

## 🚀 Render Deployment Setup

### 📋 Prerequisites
1. **Render Account**: Sign up at [render.com](https://render.com)
2. **GitHub Repository**: Push your SPA VIP code to GitHub
3. **Environment Variables**: Have your Supabase credentials ready

### 🔧 Render Configuration

#### 1️⃣ **Web Service Setup**
```yaml
Service Type: Web Service
Repository: your-github-repo/SPA_vip
Branch: main
Runtime: Python 3.11.7

Build Command: 
chmod +x build.sh && ./build.sh

Start Command:
uvicorn app:app --host 0.0.0.0 --port $PORT
```

#### 2️⃣ **Environment Variables**
Add these in Render Dashboard → Environment:
```env
SUPABASE_URL=your_supabase_project_url
SUPABASE_KEY=your_supabase_anon_key
PYTHON_VERSION=3.11.7
PORT=10000
```

#### 3️⃣ **Background Worker (Optional)**
For scheduled pipeline runs:
```yaml
Service Type: Background Worker
Start Command: python main.py --full
```

### 📦 **Dependencies Optimization**

#### ✅ **Render-Optimized Features:**
- **CPU-only PyTorch**: Faster deployment, smaller memory footprint
- **Fixed versions**: Reproducible builds
- **FastAPI integration**: Web API endpoints
- **Background tasks**: Non-blocking pipeline execution

#### 🎯 **Key Dependencies:**
```
torch==2.0.1+cpu          # CPU-optimized PyTorch
tensorflow-cpu==2.13.0    # CPU-only TensorFlow
transformers==4.35.2      # Fixed version for stability
fastapi==0.104.1          # Web framework
uvicorn==0.24.0           # ASGI server
```

### 🌐 **API Endpoints**

Once deployed, your service will have:

#### 📊 **Health & Status**
- `GET /` - Basic health check
- `GET /health` - Detailed health check
- `GET /status` - Pipeline status

#### 🚀 **Pipeline Control**
- `POST /pipeline/run` - Run full pipeline
- `POST /pipeline/crawl` - Run crawling only
- `POST /pipeline/sentiment` - Run sentiment analysis only

### 🔄 **Deployment Steps**

#### 1️⃣ **Prepare Repository**
```bash
# Add files to git
git add requirements.txt app.py build.sh render.yaml
git commit -m "Add Render deployment configuration"
git push origin main
```

#### 2️⃣ **Create Render Service**
1. Go to Render Dashboard
2. Click "New +" → "Web Service"
3. Connect your GitHub repository
4. Select the SPA_vip repository

#### 3️⃣ **Configure Service**
```yaml
Name: spa-vip-pipeline
Region: Oregon (US West)
Branch: main
Runtime: Python 3

Build Command: chmod +x build.sh && ./build.sh
Start Command: uvicorn app:app --host 0.0.0.0 --port $PORT

Instance Type: Standard (512 MB RAM, 0.5 CPU)
```

#### 4️⃣ **Set Environment Variables**
Add in Render Dashboard:
- `SUPABASE_URL`
- `SUPABASE_KEY`
- Any other custom environment variables

#### 5️⃣ **Deploy**
- Click "Create Web Service"
- Wait for build and deployment (5-10 minutes)
- Test the deployed API

### 🎯 **Usage Examples**

#### 📱 **Test Health Check**
```bash
curl https://your-app-name.onrender.com/health
```

#### 🚀 **Trigger Pipeline**
```bash
curl -X POST https://your-app-name.onrender.com/pipeline/run
```

#### 📊 **Check Status**
```bash
curl https://your-app-name.onrender.com/status
```

### ⚡ **Performance Tips**

#### 🔧 **Optimization Settings**
```python
# In your app.py, consider:
- Using smaller model variants
- Implementing caching
- Adding request timeouts
- Using async/await for I/O operations
```

#### 💾 **Memory Management**
- Standard plan: 512 MB RAM
- For heavy models, consider upgrading to Pro plan
- Monitor memory usage in Render dashboard

### 🚨 **Troubleshooting**

#### ❌ **Common Issues**
1. **Build Timeout**: Reduce dependencies or upgrade plan
2. **Memory Issues**: Use CPU-only models, upgrade instance
3. **Import Errors**: Check all dependencies in requirements.txt

#### 🔍 **Debug Commands**
```bash
# Check logs in Render dashboard
# Or use local testing:
python app.py  # Test FastAPI locally
python main.py --status  # Test main pipeline
```

### 🎉 **Success Indicators**
- ✅ Build completes without errors
- ✅ Health check returns 200 OK
- ✅ Pipeline can be triggered via API
- ✅ Database connection works
- ✅ All 5 phases execute successfully

### 🔗 **Additional Resources**
- [Render Python Docs](https://render.com/docs/python)
- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/)
- [Render Environment Variables](https://render.com/docs/environment-variables)

### 💡 **Next Steps**
1. Set up monitoring and alerting
2. Configure custom domain (optional)
3. Set up scheduled runs with cron jobs
4. Add authentication if needed
5. Implement CI/CD pipeline
