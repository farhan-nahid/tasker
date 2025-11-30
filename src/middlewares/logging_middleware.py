from fastapi import Request
from ..logging import logger
import time
import uuid


async def logging_middleware(request: Request, call_next):
    """
    Middleware for request/response logging.
    Format: timestamp | level | request_id | method | route | status | duration | ip | user_agent | message
    """
    # Generate unique request ID
    request_id = str(uuid.uuid4())[:8]
    request.state.request_id = request_id
    
    start_time = time.time()
    
    # Get client IP
    client_ip = "unknown"
    if request.client:
        client_ip = request.client.host
    elif "x-forwarded-for" in request.headers:
        client_ip = request.headers["x-forwarded-for"].split(",")[0].strip()
    elif "x-real-ip" in request.headers:
        client_ip = request.headers["x-real-ip"]
    
    # Extract user agent
    user_agent = request.headers.get("user-agent", "unknown")[:30]  # Truncate for readability
    
    try:
        response = await call_next(request)
        
        # Calculate response time in milliseconds
        duration = time.time() - start_time
        duration_ms = round(duration * 1000, 1)
        
        # Determine log level and message based on status
        if response.status_code >= 500:
            log_message = f"Server error: {response.status_code}"
            log_level = "error"
        elif response.status_code >= 400:
            log_message = f"Client error: {response.status_code}"
            log_level = "warning"
        else:
            log_message = f"Success: {response.status_code}"
            log_level = "info"
        
        # Log with all required fields
        logger.bind(
            request_id=request_id,
            method=request.method,
            route=request.url.path,
            status=response.status_code,
            duration=duration_ms,
            ip=client_ip,
            user_agent=user_agent
        ).__getattribute__(log_level)(log_message)
        
        return response
        
    except Exception as e:
        # Calculate response time for errors
        duration = time.time() - start_time
        duration_ms = round(duration * 1000, 1)
        
        # Log the error with all fields
        logger.bind(
            request_id=request_id,
            method=request.method,
            route=request.url.path,
            status=500,  # Internal server error
            duration=duration_ms,
            ip=client_ip,
            user_agent=user_agent
        ).error(f"Exception: {str(e)}")
        
        raise