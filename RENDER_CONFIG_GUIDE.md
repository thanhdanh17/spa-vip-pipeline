# 🎯 RENDER CONFIGURATION - TỪNG BƯỚC CHI TIẾT

## 📋 BƯỚC 1: TẠO RENDER ACCOUNT

### **1.1 Truy cập Render:**
```
URL: https://render.com
Click: "Get Started" hoặc "Sign Up"
```

### **1.2 Sign Up với GitHub:**
```
1. Click "Sign up with GitHub"
2. Enter GitHub credentials nếu chưa login
3. Click "Authorize Render" 
4. Complete profile setup
```

---

## 🔗 BƯỚC 2: CONNECT REPOSITORY

### **2.1 Create New Service:**
```
1. Render Dashboard → Click "New +"
2. Select "Web Service"
3. Choose "Connect a repository"
```

### **2.2 Find Your Repository:**
```
1. Search: "spa-vip-pipeline"
2. Repository: thanhdanh17/spa-vip-pipeline
3. Click "Connect"
```

**🔍 Nếu không thấy repository:**
```
1. Click "Configure GitHub App"
2. Grant access to thanhdanh17/spa-vip-pipeline
3. Return to Render and refresh
```

---

## ⚙️ BƯỚC 3: SERVICE CONFIGURATION

### **3.1 Basic Settings:**
```yaml
Name: spa-vip-pipeline
Environment: Python 3
Region: Oregon (US West)
Branch: main
```

### **3.2 Build Settings:**
```yaml
Build Command: 
chmod +x build.sh && ./build.sh

Start Command:
uvicorn app:app --host 0.0.0.0 --port $PORT

Instance Type: Standard
Auto-Deploy: Yes (default)
```

### **3.3 Advanced Settings (Optional):**
```yaml
Runtime: Python 3.11.7
Health Check Path: /health
```

---

## 🔐 BƯỚC 4: ENVIRONMENT VARIABLES

### **4.1 Trong Render Dashboard:**
```
1. Scroll down to "Environment Variables"
2. Click "Add Environment Variable"
```

### **4.2 Thêm từng biến:**

#### **SUPABASE_URL:**
```
Key: SUPABASE_URL
Value: https://baenxyqklayjtlbmubxe.supabase.co
```

#### **SUPABASE_KEY:**
```
Key: SUPABASE_KEY  
Value: [Lấy từ Supabase Dashboard]
```

**🔍 Cách lấy SUPABASE_KEY:**
```
1. Truy cập: https://supabase.com/dashboard
2. Select project
3. Settings → API
4. Copy "anon" key (NOT service_role)
```

#### **PYTHON_VERSION:**
```
Key: PYTHON_VERSION
Value: 3.11.7
```

---

## 🚀 BƯỚC 5: DEPLOY

### **5.1 Review Configuration:**
```
✅ Name: spa-vip-pipeline
✅ Repository: thanhdanh17/spa-vip-pipeline
✅ Branch: main
✅ Build Command: chmod +x build.sh && ./build.sh
✅ Start Command: uvicorn app:app --host 0.0.0.0 --port $PORT
✅ Environment Variables: 3 variables set
```

### **5.2 Start Deployment:**
```
1. Click "Create Web Service"
2. Wait for build to start
3. Monitor build logs
```

---

## 📊 BƯỚC 6: MONITOR BUILD

### **6.1 Build Process:**
```
Expected steps:
✅ Cloning repository
✅ Installing Python 3.11.7
✅ Running build command
✅ Installing dependencies from requirements.txt
✅ Creating directories
✅ Setting permissions
✅ Starting application
```

### **6.2 Success Indicators:**
```
✅ "Build successful"
✅ "Your service is live"
✅ Green status indicator
✅ Live URL available
```

---

## 🧪 BƯỚC 7: TEST DEPLOYMENT

### **7.1 Health Check:**
```
URL: https://spa-vip-pipeline.onrender.com/
Expected: {"message": "SPA VIP Pipeline API", "status": "running"}
```

### **7.2 Detailed Health:**
```
URL: https://spa-vip-pipeline.onrender.com/health
Expected: {"status": "healthy", "database": "connected"}
```

### **7.3 API Documentation:**
```
URL: https://spa-vip-pipeline.onrender.com/docs
Expected: FastAPI Swagger UI
```

---

## 🔧 TROUBLESHOOTING

### **❌ Build Failed:**

#### **Memory Error:**
```
Solution: Upgrade to Standard plan ($7/month)
Location: Service Settings → Plan
```

#### **Timeout Error:**
```
Solution: Check build.sh permissions
Command: chmod +x build.sh && ./build.sh
```

#### **Dependencies Error:**
```
Solution: Check requirements.txt
Verify all packages are available
```

### **❌ Runtime Error:**

#### **500 Internal Server Error:**
```
1. Check Environment Variables
2. Verify Supabase connection
3. Check application logs
```

#### **Database Connection Failed:**
```
1. Verify SUPABASE_URL format
2. Check SUPABASE_KEY (anon key)
3. Test connection manually
```

---

## 📋 CONFIGURATION CHECKLIST

### **Before Deploy:**
- [ ] Render account created with GitHub
- [ ] Repository connected: thanhdanh17/spa-vip-pipeline
- [ ] Service name: spa-vip-pipeline
- [ ] Build command: chmod +x build.sh && ./build.sh
- [ ] Start command: uvicorn app:app --host 0.0.0.0 --port $PORT
- [ ] SUPABASE_URL environment variable set
- [ ] SUPABASE_KEY environment variable set
- [ ] Instance Type: Standard selected

### **After Deploy:**
- [ ] Build completed successfully
- [ ] Service status: Live
- [ ] Health check returns 200 OK
- [ ] API documentation accessible
- [ ] Database connection working

---

## 🎉 SUCCESS CRITERIA

### **When deployment succeeds:**
```
✅ Build logs show "Build successful"
✅ Service status shows "Live" 
✅ URL responds: https://spa-vip-pipeline.onrender.com
✅ Health check passes
✅ API documentation loads
✅ No error messages in logs
```

---

## 📞 NEXT STEPS AFTER SUCCESS

### **Immediate:**
1. Test all API endpoints
2. Trigger a pipeline run
3. Monitor performance
4. Set up notifications

### **Optional:**
1. Custom domain setup
2. SSL certificate (auto-provided)
3. Scaling configuration
4. Monitoring setup

---

**🚀 BẮT ĐẦU NGAY: https://render.com**

**⏰ Estimated time: 10-15 minutes total**
