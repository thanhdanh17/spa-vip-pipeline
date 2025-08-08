# 🚀 SPA VIP - HƯỚNG DẪN DEPLOY RENDER TỪNG BƯỚC

## 📋 CHECKLIST TRƯỚC KHI DEPLOY

### ✅ **Bước 1: Kiểm tra Environment Variables**
```bash
# Mở file .env và đảm bảo có đầy đủ:
SUPABASE_URL=your_supabase_project_url
SUPABASE_KEY=your_supabase_anon_key
```

### ✅ **Bước 2: Test Local**
```bash
# Test requirements.txt
pip install -r requirements.txt

# Test main pipeline
python main.py --status

# Test FastAPI app
python app.py
# Mở browser: http://localhost:8000
```

---

## 🌐 BƯỚC 1: CHUẨN BỊ GITHUB REPOSITORY

### 📤 **Push code lên GitHub:**
```bash
# Tạo repo mới trên GitHub: spa-vip-pipeline

# Trong terminal SPA_vip:
git init
git add .
git commit -m "🚀 Initial commit - SPA VIP ready for Render"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/spa-vip-pipeline.git
git push -u origin main
```

---

## 🎯 BƯỚC 2: TẠO RENDER SERVICE

### 1️⃣ **Đăng ký Render:**
- Truy cập: https://render.com
- Sign up với GitHub account
- Authorize Render to access repositories

### 2️⃣ **Tạo Web Service:**
```
Dashboard → New + → Web Service
```

### 3️⃣ **Connect Repository:**
```
Repository: spa-vip-pipeline
Branch: main
```

### 4️⃣ **Configure Service:**
```yaml
Name: spa-vip-pipeline
Environment: Python 3
Region: Oregon (US West)
Instance Type: Standard ($7/month)

Build Command: 
chmod +x build.sh && ./build.sh

Start Command:
uvicorn app:app --host 0.0.0.0 --port $PORT
```

---

## 🔐 BƯỚC 3: SETUP ENVIRONMENT VARIABLES

### **Trong Render Dashboard → Environment:**
```env
SUPABASE_URL = https://your-project.supabase.co
SUPABASE_KEY = your_anon_key
PYTHON_VERSION = 3.11.7
```

**⚠️ LƯU Ý:** Không để trailing spaces trong values!

---

## 🚀 BƯỚC 4: DEPLOY & TEST

### 1️⃣ **Start Deployment:**
- Click "Create Web Service"
- Wait 5-10 minutes for build

### 2️⃣ **Monitor Build:**
```
Logs → Build Logs
# Kiểm tra không có errors
```

### 3️⃣ **Test Endpoints:**
```bash
# Health check
curl https://spa-vip-pipeline.onrender.com/health

# System status  
curl https://spa-vip-pipeline.onrender.com/status

# Trigger pipeline
curl -X POST https://spa-vip-pipeline.onrender.com/pipeline/run
```

---

## 🔧 BƯỚC 5: TROUBLESHOOTING

### ❌ **Nếu Build Failed:**
```bash
# Check logs for common issues:
1. Missing dependencies → Update requirements.txt
2. Memory issues → Upgrade to Standard plan
3. Timeout → Optimize build.sh
```

### ❌ **Nếu Runtime Error:**
```bash
# Check environment variables
# Verify Supabase connection
# Check model files exist
```

---

## 📊 BƯỚC 6: MONITORING & MAINTENANCE

### 🔍 **Health Monitoring:**
```bash
# Set up uptime monitoring:
curl https://spa-vip-pipeline.onrender.com/health
```

### 🔄 **Auto Redeploy:**
```bash
# Render tự động redeploy khi push code mới
git add .
git commit -m "Update features"
git push origin main
```

---

## 🎯 CÁC LỆNH CẦN CHẠY NGAY BÂY GIỜ:

### **1. Test local trước:**
```bash
cd D:\SPA_vip
python -m pip install -r requirements.txt
python app.py
```

### **2. Chuẩn bị Git:**
```bash
git init
git add .
git commit -m "🚀 SPA VIP ready for Render deployment"
```

### **3. Kiểm tra .env:**
```bash
# Mở .env và verify Supabase credentials
notepad .env
```

---

## 🎉 SAU KHI DEPLOY THÀNH CÔNG:

### **API Endpoints available:**
- `GET /` - Health check
- `GET /health` - Detailed status
- `GET /status` - Pipeline status
- `POST /pipeline/run` - Run full pipeline
- `POST /pipeline/crawl` - Crawl only
- `POST /pipeline/sentiment` - Sentiment only

### **Scheduled runs (optional):**
```bash
# Set up GitHub Actions for cron jobs
# Or use Render cron jobs
```

---

## 🚨 QUAN TRỌNG - ĐỌC TRƯỚC KHI DEPLOY:

1. **💰 Chi phí:** Standard plan $7/month
2. **⏰ Sleep:** Free tier sleeps sau 15 phút inactive
3. **💾 Storage:** 1GB disk space limit
4. **🔄 Build time:** 5-10 phút mỗi lần deploy
5. **📊 Models:** AI models phải < 100MB mỗi file

---

## 🎯 BƯỚC TIẾP THEO CỦA BẠN:

**NGAY BÂY GIỜ:**
1. ✅ Test local: `python app.py`
2. ✅ Check .env file
3. ✅ Create GitHub repo
4. ✅ Push code to GitHub

**SAU ĐÓ:**
5. ✅ Create Render account
6. ✅ Connect GitHub repo
7. ✅ Configure & deploy
8. ✅ Test deployed app

Bạn muốn tôi hướng dẫn chi tiết bước nào trước? 🤔
