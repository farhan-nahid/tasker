"""
HTTP Request Logging Middleware.

This middleware automatically logs all HTTP requests and responses
with detailed context information. It generates unique request IDs
for tracking and includes performance timing.

Logged Information:
- Request ID: Unique identifier for request tracking
- Method: HTTP method (GET, POST, PUT, DELETE, etc.)
- Route: Request path/endpoint
- Status: HTTP response status code
- Duration: Request processing time in milliseconds
- IP Address: Client IP (supports proxies via X-Forwarded-For)
- User Agent: Client browser/application info (truncated)

The middleware integrates with the centralized logging system
and provides structured logging for monitoring and debugging.
"""

from fastapi import Request, Response
from ..logging import logger
import time
import uuid
from typing import Callable, Awaitable


async def logging_middleware(
    request: Request, 
    call_next: Callable[[Request], Awaitable[Response]]
) -> Response:
    """
    Log HTTP requests and responses with detailed context.
    
    Automatically captures request information, processes the request,
    and logs the outcome with timing and context data. Handles both
    successful requests and exceptions gracefully.
    
    Args:
        request (Request): FastAPI request object
        call_next (Callable): Next middleware/handler in the chain
        
    Returns:
        Response: HTTP response from the downstream handler
        
    Raises:
        Exception: Re-raises any exceptions after logging them
        
    Format:
        timestamp | level | request_id | method | route | status | duration | ip | user_agent | message
        
    Example Log Output:
        2025-11-30 20:15:32 | INFO     | abc12345 | GET    | /api/users              | 200 |   45.2ms | 127.0.0.1       | Mozilla/5.0... | Success: 200
        2025-11-30 20:15:45 | ERROR    | def67890 | POST   | /api/users              | 500 |  123.7ms | 192.168.1.100   | PostmanRuntime... | Exception: Database connection failed
    """
    # Generate unique 8-character request ID for tracking
    request_id = str(uuid.uuid4())[:8]
    request.state.request_id = request_id
    
    # Record start time for duration calculation
    start_time = time.time()
    
    # Extract client IP address with proxy support
    client_ip = _extract_client_ip(request)
    
    # Get and truncate user agent for readability
    user_agent = request.headers.get("user-agent", "unknown")[:30]
    
    try:
        # Process the request through the application
        response = await call_next(request)
        
        # Calculate total request processing time
        duration = time.time() - start_time
        duration_ms = round(duration * 1000, 1)
        
        # Determine log level and message based on HTTP status
        log_level, log_message = _get_log_info(response.status_code)
        
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


def _extract_client_ip(request: Request) -> str:
    """
    Extract client IP address with proxy header support.
    
    Checks multiple sources for the real client IP:
    1. Direct connection (request.client.host)
    2. X-Forwarded-For header (load balancer/proxy)
    3. X-Real-IP header (nginx proxy)
    
    Args:
        request (Request): FastAPI request object
        
    Returns:
        str: Client IP address or "unknown" if not found
    """
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


def _get_log_info(status_code: int) -> tuple[str, str]:
    """
    Determine appropriate log level and message for HTTP status code.
    
    Args:
        status_code (int): HTTP response status code
        
    Returns:
        tuple[str, str]: (log_level, log_message) for the status
        
    Examples:
        200 -> ("info", "Success: 200")
        404 -> ("warning", "Client error: 404")
        500 -> ("error", "Server error: 500")
    """
    if status_code >= 500:
        return "error", f"Server error: {status_code}"
    elif status_code >= 400:
        return "warning", f"Client error: {status_code}"
    else:
        return "info", f"Success: {status_code}"


# Export middleware function for use in FastAPI app
__all__ = ["logging_middleware"]