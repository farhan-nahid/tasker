from fastapi import Request, Response
from ..utils.logging import logger
import time
import uuid
from typing import Callable, Awaitable


async def logging_middleware(
    request: Request, 
    call_next: Callable[[Request], Awaitable[Response]]
) -> Response:
    # Generate unique 8-character request ID for tracking
    request_id = str(uuid.uuid4())[:8]
    request.state.request_id = request_id
    
    # Record start time for duration calculation
    start_time = time.time()
    
    # Extract client IP address with proxy support
    client_ip = extract_client_ip(request)
    
    # Get and truncate user agent for readability
    user_agent = request.headers.get("user-agent", "unknown")[:30]
    
    try:
        # Process the request through the application
        response = await call_next(request)
        
        # Calculate total request processing time
        duration = time.time() - start_time
        duration_ms = round(duration * 1000, 1)
        
        # Determine log level and message based on HTTP status
        log_level, log_message = get_log_info(response.status_code)
        
        # Log request with full context using structured logging
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
        # Calculate duration even for failed requests
        duration = time.time() - start_time
        duration_ms = round(duration * 1000, 1)
        
        # Log the exception with full context
        logger.bind(
            request_id=request_id,
            method=request.method,
            route=request.url.path,
            status=500,  # Internal server error for exceptions
            duration=duration_ms,
            ip=client_ip,
            user_agent=user_agent
        ).error(f"Exception: {str(e)}")
        
        # Re-raise the exception to be handled by error handlers
        raise


def extract_client_ip(request: Request) -> str:
    # Try direct connection first
    if request.client:
        return request.client.host
    
    # Check X-Forwarded-For header (comma-separated list)
    forwarded_for = request.headers.get("x-forwarded-for")
    if forwarded_for:
        # Take first IP from comma-separated list
        return forwarded_for.split(",")[0].strip()
    
    # Check X-Real-IP header (single IP)
    real_ip = request.headers.get("x-real-ip")
    if real_ip:
        return real_ip
    
    # Default fallback
    return "unknown"


def get_log_info(status_code: int) -> tuple[str, str]:
    if status_code >= 500:
        return "error", f"Server error: {status_code}"
    elif status_code >= 400:
        return "warning", f"Client error: {status_code}"
    else:
        return "info", f"Success: {status_code}"
