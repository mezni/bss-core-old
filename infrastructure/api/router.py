from fastapi import FastAPI, APIRouter, Depends, HTTPException, status, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import structlog

from infrastructure.security.jwt import get_current_user

logger = structlog.get_logger()

app = FastAPI(
    title="Shipment Management API",
    description="BSS-Core Shipment Management Module",
    version="1.0.0",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    structlog.contextvars.bind_contextvars(
        method=request.method,
        path=request.url.path,
        client_host=request.client.host,
        client_port=request.client.port,
    )
    response = await call_next(request)
    structlog.contextvars.bind_contextvars(
        status_code=response.status_code,
    )
    logger.info("HTTP request completed")
    return response

# Global exception handler
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )

# Root endpoint
@app.get("/")
async def root():
    return {"message": "Shipment Management API", "version": "1.0.0"}