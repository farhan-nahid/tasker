from fastapi import FastAPI, Request, Depends
from .configs.database import get_db
from .logging import configure_logging, LogLevels, logger
import time
from src.configs.app_vars import PORT


# Configure Loguru logging
configure_logging(LogLevels.INFO)

# Log application startup
logger.info("Server starting on http://localhost:{}".format(PORT))

app = FastAPI(
    title="Tasker API",
    description="Professional Task Management API",
    version="1.0.0",
    dependencies=[Depends(get_db)]
)

# Middleware for request/response logging
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    
    # Get client IP
    client_ip = "unknown"
    if request.client:
        client_ip = request.client.host
    elif "x-forwarded-for" in request.headers:
        client_ip = request.headers["x-forwarded-for"].split(",")[0].strip()
    elif "x-real-ip" in request.headers:
        client_ip = request.headers["x-real-ip"]
    
    try:
        response = await call_next(request)
        
        # Calculate response time in milliseconds
        duration = time.time() - start_time
        response_time = round(duration * 1000, 1)
        
        # Log with Loguru using bind for extra context
        if response.status_code >= 500:
            logger.bind(
                ip=client_ip,
                method=request.method,
                route=request.url.path,
                response_time=response_time
            ).error(f"Server error: {response.status_code}")
        elif response.status_code >= 400:
            logger.bind(
                ip=client_ip,
                method=request.method,
                route=request.url.path,
                response_time=response_time
            ).warning(f"Client error: {response.status_code}")
        else:
            logger.bind(
                ip=client_ip,
                method=request.method,
                route=request.url.path,
                response_time=response_time
            ).info(f"Success: {response.status_code}")
        
        return response
        
    except Exception as e:
        # Calculate response time for errors
        duration = time.time() - start_time
        response_time = round(duration * 1000, 1)
        
        # Log the error
        logger.bind(
            ip=client_ip,
            method=request.method,
            route=request.url.path,
            response_time=response_time
        ).error(f"Exception: {str(e)}")
        
        raise


@app.get("/")
async def read_root():
    """Root endpoint."""
    return {
        "message": "Welcome to Tasker API",
        "version": "1.0.0",
        "status": "healthy"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": time.time()
    }