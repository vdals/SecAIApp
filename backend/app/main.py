import logging
import uvicorn
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
from loguru import logger
from fastapi.security import OAuth2PasswordBearer
from fastapi.routing import APIRoute
from alembic.config import Config
from alembic import command

from app.auth.router import router as auth_router
from app.users.router import router as users_router
from app.locations.router import router as locations_router
from app.cameras.router import router as cameras_router
from app.videos.router import router as videos_router
from app.events.router import router as events_router
from app.config import settings

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    docs_url=f"{settings.API_PREFIX}/docs",
    redoc_url=f"{settings.API_PREFIX}/redoc",
    openapi_url=f"{settings.API_PREFIX}/openapi.json",
    debug=settings.DEBUG
)

# Configure OAuth2 for Swagger UI
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_PREFIX}/auth/login/form")

# Fix problem with arguments in OpenAPI
for route in app.routes:
    if isinstance(route, APIRoute):
        # Remove all "optional" parameters from the specification
        route.dependant.query_params = [
            param for param in route.dependant.query_params 
            if param.name not in ["args", "kwargs"]
        ]

app.swagger_ui_init_oauth = {
    "usePkceWithAuthorizationCodeGrant": False,
    "useBasicAuthenticationWithAccessCodeGrant": False,
    "clientId": "swagger"
}

# Define security scheme
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description="Система видеонаблюдения с ИИ",
        routes=app.routes,
    )
    
    # Add security component
    openapi_schema["components"] = openapi_schema.get("components", {})
    openapi_schema["components"]["securitySchemes"] = {
        "bearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        },
        "OAuth2PasswordBearer": {
            "type": "oauth2",
            "flows": {
                "password": {
                    "tokenUrl": f"{settings.API_PREFIX}/auth/login/form",
                    "scopes": {}
                }
            }
        }
    }
    
    # Use default security
    openapi_schema["security"] = [{"bearerAuth": []}, {"OAuth2PasswordBearer": []}]
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix=settings.API_PREFIX)
app.include_router(users_router, prefix=settings.API_PREFIX)
app.include_router(locations_router, prefix=settings.API_PREFIX)
app.include_router(cameras_router, prefix=settings.API_PREFIX)
app.include_router(videos_router, prefix=settings.API_PREFIX)
app.include_router(events_router, prefix=settings.API_PREFIX)

# Logging requests
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """
    Middleware for logging requests
    """
    logger.info(f"{request.method} {request.url.path}")
    response = await call_next(request)
    return response

# Error handling
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Global exception handler
    """
    logger.error(f"Unexpected error: {str(exc)}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error"},
    )

# Health check route
@app.get(f"{settings.API_PREFIX}/health", tags=["health"])
async def health_check():
    """
    Check API health
    """
    return {"status": "ok", "version": settings.VERSION}

# Create necessary directories
import os
os.makedirs("uploads/videos", exist_ok=True)
os.makedirs("uploads/frames", exist_ok=True)
os.makedirs("logs", exist_ok=True)

# Configure logging
logger.add(
    "logs/app.log",
    rotation="10 MB",
    level=settings.LOG_LEVEL,
    format="{time} | {level} | {message}",
)

# Message about application start
logger.info(f"Starting {settings.PROJECT_NAME} v{settings.VERSION}")
logger.info(f"Debug mode: {settings.DEBUG}")

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True) 