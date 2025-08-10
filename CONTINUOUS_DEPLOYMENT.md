# 🚀 SPA VIP - Continuous Deployment Guide

## 📖 Overview
This guide explains how to deploy SPA VIP Pipeline to run continuously on Render with automated scheduling.

## 🏗️ Deployment Options

### Option 1: Built-in Scheduler (Recommended)
The FastAPI app includes a built-in scheduler that runs automatically:

#### Features:
- ✅ Crawl every 1 hour
- ✅ Sentiment analysis every 4 hours  
- ✅ Full pipeline daily at 2:00 AM
- ✅ Built-in API endpoints for control

#### Endpoints:
```
GET  /scheduler/status     - Check scheduler status
POST /scheduler/start      - Start scheduler
POST /scheduler/stop       - Stop scheduler
POST /schedule/crawl       - Trigger crawl now
POST /schedule/sentiment   - Trigger sentiment now
POST /schedule/full        - Trigger full pipeline now
```

### Option 2: Dedicated Worker Service
Deploy separate scheduler as worker service for better resource isolation.

## 🔧 Setup Instructions

### 1. Update Environment Variables
In Render Dashboard, set these environment variables:

```bash
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
API_BASE_URL=https://your-app-name.onrender.com
```

### 2. Deploy Options

#### A. Single Service (Web Only)
Use current `render.yaml` configuration - scheduler runs within web service.

#### B. Two Services (Web + Worker)
Update `render.yaml` to include worker service for dedicated scheduling.

### 3. Monitor Operations

#### Check Scheduler Status:
```bash
curl https://your-app.onrender.com/scheduler/status
```

#### Trigger Jobs Manually:
```bash
# Trigger crawl
curl -X POST https://your-app.onrender.com/schedule/crawl

# Trigger sentiment
curl -X POST https://your-app.onrender.com/schedule/sentiment

# Trigger full pipeline
curl -X POST https://your-app.onrender.com/schedule/full
```

#### View Logs:
Go to Render Dashboard → Your Service → Logs tab

## ⏰ Schedule Configuration

Current schedule (can be modified in `app.py`):

```python
schedule.every(1).hours.do(scheduled_crawl)           # Every hour
schedule.every(4).hours.do(scheduled_sentiment)       # Every 4 hours  
schedule.every().day.at("02:00").do(scheduled_full)   # Daily at 2 AM
```

## 🎛️ Control & Monitoring

### Available Endpoints:
- `GET /` - Health check
- `GET /health` - Detailed health check
- `GET /status` - Pipeline status
- `GET /models/status` - AI models status
- `GET /scheduler/status` - Scheduler status
- `POST /pipeline/run` - Run full pipeline
- `POST /pipeline/crawl` - Run crawl only
- `POST /pipeline/sentiment` - Run sentiment only

### Manual Control:
```bash
# Stop scheduler
curl -X POST https://your-app.onrender.com/scheduler/stop

# Start scheduler  
curl -X POST https://your-app.onrender.com/scheduler/start

# Check what's scheduled
curl https://your-app.onrender.com/scheduler/status
```

## 🚨 Troubleshooting

### Scheduler Not Running:
1. Check logs: Render Dashboard → Logs
2. Restart scheduler: `POST /scheduler/start`
3. Check status: `GET /scheduler/status`

### Jobs Failing:
1. Check database connection: `GET /health`
2. Check models: `GET /models/status`
3. Check environment variables in Render Dashboard

### High Resource Usage:
1. Consider using Worker service for scheduler
2. Adjust schedule frequency
3. Monitor Render metrics

## 📊 Monitoring & Logs

### Key Log Messages:
- `🚀 Scheduler started!` - Scheduler initialized
- `🕒 Scheduled [job] started` - Job execution
- `✅ [job] completed` - Job success
- `❌ [job] failed` - Job failure

### Health Checks:
The app includes automatic health monitoring:
- Database connectivity
- Model availability  
- Service status

## 🔄 Deployment Commands

### Initial Deploy:
```bash
git add .
git commit -m "Add continuous scheduling"
git push origin main
```

### Update Schedule:
1. Modify schedule in `app.py`
2. Commit and push changes
3. Render will auto-deploy

## 💡 Best Practices

1. **Monitor Resource Usage**: Check Render metrics regularly
2. **Error Handling**: Jobs include retry logic and fallbacks
3. **Logging**: All operations are logged for debugging
4. **Graceful Shutdowns**: Scheduler stops cleanly on app restart
5. **Manual Override**: Can trigger jobs manually anytime

## 🎯 Next Steps

1. Deploy to Render
2. Check scheduler status at `/scheduler/status`
3. Monitor first few job executions
4. Adjust schedule if needed
5. Set up monitoring alerts (optional)

Your pipeline will now run continuously on Render! 🚀
