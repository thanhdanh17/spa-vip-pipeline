#!/usr/bin/env python3
"""
SPA VIP - Render Web App Entry Point
FastAPI application for web deployment on Render
"""

from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.responses import JSONResponse
import subprocess
import logging
import os
from datetime import datetime
import asyncio

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="SPA VIP Pipeline",
    description="Vietnamese Stock Price Analysis & VIP Pipeline API",
    version="1.0.0"
)

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "SPA VIP Pipeline API",
        "status": "running",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }

@app.get("/health")
async def health_check():
    """Detailed health check"""
    try:
        # Test database connection
        result = subprocess.run(
            ["python", "database/test_connection.py"],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        db_status = "connected" if result.returncode == 0 else "error"
        
        # Check model availability
        model_status = {}
        try:
            from models.model_manager import get_model_manager
            manager = get_model_manager()
            model_status = manager.check_all_models()
        except Exception as e:
            model_status = {"error": str(e)}
        
        return {
            "status": "healthy",
            "database": db_status,
            "models": model_status,
            "timestamp": datetime.now().isoformat(),
            "services": {
                "crawling": "available",
                "summarization": "available", 
                "sentiment": "available",
                "timeseries": "available",
                "industry": "available"
            }
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            status_code=503,
            content={"status": "unhealthy", "error": str(e)}
        )

@app.post("/pipeline/run")
async def run_pipeline(background_tasks: BackgroundTasks):
    """Run the complete SPA VIP pipeline"""
    background_tasks.add_task(run_full_pipeline)
    return {
        "message": "Pipeline started",
        "status": "running",
        "timestamp": datetime.now().isoformat()
    }

@app.post("/pipeline/crawl")
async def run_crawl_only(background_tasks: BackgroundTasks):
    """Run only the crawling phase"""
    background_tasks.add_task(run_crawl_pipeline)
    return {
        "message": "Crawling started",
        "status": "running",
        "timestamp": datetime.now().isoformat()
    }

@app.post("/pipeline/sentiment")
async def run_sentiment_only(background_tasks: BackgroundTasks):
    """Run only sentiment analysis"""
    background_tasks.add_task(run_sentiment_pipeline)
    return {
        "message": "Sentiment analysis started",
        "status": "running",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/status")
async def get_status():
    """Get pipeline status"""
    try:
        result = subprocess.run(
            ["python", "main.py", "--status"],
            capture_output=True,
            text=True,
            timeout=60
        )
        
        return {
            "status": "success",
            "output": result.stdout,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Status check failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

async def run_full_pipeline():
    """Background task to run full pipeline"""
    try:
        logger.info("Starting full pipeline...")
        result = subprocess.run(
            ["python", "main.py", "--full"],
            capture_output=True,
            text=True,
            timeout=3600  # 1 hour timeout
        )
        logger.info(f"Pipeline completed with exit code: {result.returncode}")
    except Exception as e:
        logger.error(f"Pipeline failed: {e}")

async def run_crawl_pipeline():
    """Background task to run crawling only"""
    try:
        logger.info("Starting crawl pipeline...")
        result = subprocess.run(
            ["python", "main.py", "--crawl-only"],
            capture_output=True,
            text=True,
            timeout=1800  # 30 minutes timeout
        )
        logger.info(f"Crawl completed with exit code: {result.returncode}")
    except Exception as e:
        logger.error(f"Crawl failed: {e}")

async def run_sentiment_pipeline():
    """Background task to run sentiment analysis only"""
    try:
        logger.info("Starting sentiment pipeline...")
        result = subprocess.run(
            ["python", "main.py", "--sentiment-only"],
            capture_output=True,
            text=True,
            timeout=600  # 10 minutes timeout
        )
        logger.info(f"Sentiment analysis completed with exit code: {result.returncode}")
    except Exception as e:
        logger.error(f"Sentiment analysis failed: {e}")

@app.post("/models/download")
async def download_models(background_tasks: BackgroundTasks):
    """Download all AI models from Hugging Face"""
    background_tasks.add_task(run_model_download)
    return {"message": "Model download started", "status": "in_progress"}

@app.get("/models/status")
async def models_status():
    """Check status of AI models"""
    try:
        from models.model_manager import get_model_manager
        manager = get_model_manager()
        status = manager.check_all_models()
        
        all_available = all(status.values())
        
        return {
            "models": status,
            "all_available": all_available,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error checking models: {str(e)}")

async def run_model_download():
    """Background task to download all models"""
    try:
        logger.info("Starting model download...")
        result = subprocess.run(
            ["python", "download_models.py", "--all"],
            capture_output=True,
            text=True,
            timeout=1800  # 30 minutes timeout
        )
        logger.info(f"Model download completed with exit code: {result.returncode}")
    except Exception as e:
        logger.error(f"Model download failed: {e}")

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
