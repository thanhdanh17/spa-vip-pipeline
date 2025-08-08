# ✅ RENDER DEPLOYMENT CHECKLIST - thanhdanh17/spa-vip-pipeline

## 🎯 PHASE 1: RENDER ACCOUNT SETUP

### ☐ **Step 1.1: Create Account**
- [ ] Go to https://render.com
- [ ] Click "Get Started" or "Sign Up"
- [ ] Choose "Sign up with GitHub"
- [ ] Authorize Render to access GitHub

### ☐ **Step 1.2: Repository Access**
- [ ] Grant Render access to thanhdanh17/spa-vip-pipeline
- [ ] Confirm repository is visible in Render

---

## 🎯 PHASE 2: WEB SERVICE CREATION

### ☐ **Step 2.1: Create Service**
- [ ] Dashboard → "New +" → "Web Service"
- [ ] Choose "Connect a repository"
- [ ] Find and select: thanhdanh17/spa-vip-pipeline
- [ ] Click "Connect"

### ☐ **Step 2.2: Basic Configuration**
```
Service Name: spa-vip-pipeline
Environment: Python 3
Region: Oregon (US West)
Branch: main
```
- [ ] Service name entered
- [ ] Environment selected
- [ ] Region selected
- [ ] Branch confirmed

---

## 🎯 PHASE 3: BUILD CONFIGURATION

### ☐ **Step 3.1: Commands**
```
Build Command: chmod +x build.sh && ./build.sh
Start Command: uvicorn app:app --host 0.0.0.0 --port $PORT
```
- [ ] Build command entered exactly
- [ ] Start command entered exactly
- [ ] Commands verified (no typos)

### ☐ **Step 3.2: Plan Selection**
- [ ] Instance Type: Standard ($7/month)
- [ ] Auto-Deploy: Enabled (default)

---

## 🎯 PHASE 4: ENVIRONMENT VARIABLES

### ☐ **Step 4.1: Add Variables**
**Variable 1:**
```
Key: SUPABASE_URL
Value: https://baenxyqklayjtlbmubxe.supabase.co
```
- [ ] Key entered correctly
- [ ] Value entered correctly
- [ ] No extra spaces

**Variable 2:**
```
Key: SUPABASE_KEY
Value: [Get from Supabase Dashboard → Settings → API → anon key]
```
- [ ] Key entered correctly
- [ ] Anon key copied (NOT service_role)
- [ ] Value pasted correctly

**Variable 3:**
```
Key: PYTHON_VERSION
Value: 3.11.7
```
- [ ] Key entered correctly
- [ ] Value entered correctly

### ☐ **Step 4.2: Verify Variables**
- [ ] Total 3 environment variables
- [ ] All keys spelled correctly
- [ ] All values entered without extra spaces
- [ ] No sensitive data in logs

---

## 🎯 PHASE 5: DEPLOY

### ☐ **Step 5.1: Final Review**
```
✅ Name: spa-vip-pipeline
✅ Repo: thanhdanh17/spa-vip-pipeline
✅ Branch: main
✅ Build: chmod +x build.sh && ./build.sh
✅ Start: uvicorn app:app --host 0.0.0.0 --port $PORT
✅ Plan: Standard
✅ Env vars: 3 variables
```
- [ ] All settings reviewed
- [ ] Configuration looks correct

### ☐ **Step 5.2: Launch**
- [ ] Click "Create Web Service"
- [ ] Deployment started
- [ ] Build logs visible

---

## 🎯 PHASE 6: MONITOR BUILD

### ☐ **Step 6.1: Build Progress**
Expected log entries:
- [ ] "Cloning repository"
- [ ] "Installing Python"
- [ ] "Running build command"
- [ ] "Installing dependencies"
- [ ] "Build successful"

### ☐ **Step 6.2: Start Application**
- [ ] "Starting application"
- [ ] "Your service is live"
- [ ] Green status indicator
- [ ] URL available

---

## 🎯 PHASE 7: TESTING

### ☐ **Step 7.1: Basic Health Check**
URL: `https://spa-vip-pipeline.onrender.com/`
- [ ] Opens successfully
- [ ] Returns JSON response
- [ ] Shows "status": "running"

### ☐ **Step 7.2: Detailed Health**
URL: `https://spa-vip-pipeline.onrender.com/health`
- [ ] Opens successfully
- [ ] Shows "status": "healthy"
- [ ] Shows "database": "connected"

### ☐ **Step 7.3: API Documentation**
URL: `https://spa-vip-pipeline.onrender.com/docs`
- [ ] FastAPI Swagger UI loads
- [ ] All endpoints visible
- [ ] Interactive documentation works

---

## 🎯 PHASE 8: PIPELINE TESTING

### ☐ **Step 8.1: System Status**
URL: `https://spa-vip-pipeline.onrender.com/status`
- [ ] Returns system statistics
- [ ] Shows database counts
- [ ] No error messages

### ☐ **Step 8.2: Pipeline Trigger (Optional)**
```bash
curl -X POST https://spa-vip-pipeline.onrender.com/pipeline/crawl
```
- [ ] Returns success message
- [ ] Background task started
- [ ] No immediate errors

---

## 🚨 TROUBLESHOOTING CHECKLIST

### ☐ **If Build Fails:**
- [ ] Check build logs for specific error
- [ ] Verify build command: `chmod +x build.sh && ./build.sh`
- [ ] Ensure Standard plan selected (not Free)
- [ ] Check GitHub repository permissions

### ☐ **If Runtime Fails:**
- [ ] Verify environment variables spelling
- [ ] Check SUPABASE_KEY is anon key (not service_role)
- [ ] Verify start command: `uvicorn app:app --host 0.0.0.0 --port $PORT`
- [ ] Check application logs for errors

### ☐ **If Health Check Fails:**
- [ ] Verify Supabase connection
- [ ] Check environment variables values
- [ ] Test database connectivity
- [ ] Review application logs

---

## 🎉 SUCCESS CRITERIA

### ☐ **Deployment Complete When:**
- [ ] Build status: Success
- [ ] Service status: Live  
- [ ] Health check: Passing
- [ ] API docs: Accessible
- [ ] No error logs
- [ ] URL responds correctly

---

## 📞 IMMEDIATE NEXT STEPS

### ☐ **After Successful Deployment:**
- [ ] Bookmark the live URL
- [ ] Test all main endpoints
- [ ] Monitor first pipeline run
- [ ] Set up monitoring/alerts
- [ ] Document the deployment

### ☐ **Share Results:**
- [ ] Note the live URL: https://spa-vip-pipeline.onrender.com
- [ ] Verify all 5 pipeline phases work
- [ ] Test API integration capabilities
- [ ] Confirm production readiness

---

**🚀 START HERE: https://render.com**

**⏰ ESTIMATED TIME: 15-20 minutes**

**🎯 GOAL: Live API at https://spa-vip-pipeline.onrender.com**
