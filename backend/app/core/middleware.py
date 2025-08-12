import time
import logging
from typing import Callable
from fastapi import Request, Response, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

logger = logging.getLogger(__name__)

class LoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware for logging HTTP requests and responses
    """
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()
        
        # Log request
        logger.info(f"Request: {request.method} {request.url}")
        
        try:
            response = await call_next(request)
            
            # Calculate processing time
            process_time = time.time() - start_time
            
            # Log response
            logger.info(
                f"Response: {response.status_code} - "
                f"Time: {process_time:.3f}s - "
                f"Path: {request.url.path}"
            )
            
            # Add processing time to response headers
            response.headers["X-Process-Time"] = str(process_time)
            
            return response
            
        except Exception as e:
            process_time = time.time() - start_time
            logger.error(
                f"Request failed: {request.method} {request.url} - "
                f"Error: {str(e)} - "
                f"Time: {process_time:.3f}s"
            )
            raise

class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    """
    Middleware for global error handling
    """
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        try:
            response = await call_next(request)
            return response
            
        except HTTPException as e:
            # Let FastAPI handle HTTP exceptions normally
            raise
            
        except Exception as e:
            logger.error(f"Unhandled exception: {str(e)}", exc_info=True)
            
            return JSONResponse(
                status_code=500,
                content={
                    "error": "Internal server error",
                    "message": "An unexpected error occurred",
                    "type": "server_error"
                }
            )

class CacheControlMiddleware(BaseHTTPMiddleware):
    """
    Middleware for adding cache control headers
    """
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)
        
        # Add cache control headers based on endpoint
        path = request.url.path
        
        if path.startswith("/api/v1/players") or path.startswith("/api/v1/teams"):
            # Cache player and team data for 5 minutes
            response.headers["Cache-Control"] = "public, max-age=300"
        elif path.startswith("/api/v1/fixtures"):
            # Cache fixture data for 1 minute
            response.headers["Cache-Control"] = "public, max-age=60"
        elif path.startswith("/api/v1/stats"):
            # Cache stats for 10 minutes
            response.headers["Cache-Control"] = "public, max-age=600"
        elif path.startswith("/api/v1/recommendations"):
            # Don't cache recommendations
            response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        else:
            # Default cache for other endpoints
            response.headers["Cache-Control"] = "public, max-age=60"
        
        return response

class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Simple rate limiting middleware
    Note: In production, use Redis-based rate limiting
    """
    
    def __init__(self, app: ASGIApp, requests_per_minute: int = 60):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.request_counts = {}
        self.last_reset = time.time()
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Reset counts every minute
        current_time = time.time()
        if current_time - self.last_reset > 60:
            self.request_counts.clear()
            self.last_reset = current_time
        
        # Get client IP
        client_ip = request.client.host if request.client else "unknown"
        
        # Check rate limit
        current_count = self.request_counts.get(client_ip, 0)
        
        if current_count >= self.requests_per_minute:
            return JSONResponse(
                status_code=429,
                content={
                    "error": "Rate limit exceeded",
                    "message": f"Maximum {self.requests_per_minute} requests per minute allowed",
                    "type": "rate_limit_error"
                }
            )
        
        # Increment count
        self.request_counts[client_ip] = current_count + 1
        
        response = await call_next(request)
        
        # Add rate limit headers
        response.headers["X-RateLimit-Limit"] = str(self.requests_per_minute)
        response.headers["X-RateLimit-Remaining"] = str(
            max(0, self.requests_per_minute - self.request_counts[client_ip])
        )
        
        return response

def setup_middleware(app):
    """
    Setup all middleware for the FastAPI app
    """
    from app.core.config import settings
    
    # Add CORS middleware
    from fastapi.middleware.cors import CORSMiddleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.BACKEND_CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Add custom middleware
    if settings.DEBUG:
        app.add_middleware(LoggingMiddleware)
    
    app.add_middleware(ErrorHandlingMiddleware)
    app.add_middleware(CacheControlMiddleware)
    
    # Add rate limiting in production
    if not settings.DEBUG:
        app.add_middleware(RateLimitMiddleware, requests_per_minute=120)
    
    logger.info("Middleware setup completed")
