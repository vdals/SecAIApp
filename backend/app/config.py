from typing import Any, Dict, List, Optional
from pydantic import PostgresDsn, field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "Video Surveillance API"
    API_PREFIX: str = "/api"
    DEBUG: bool = False
    VERSION: str = "0.1.0"
    
    # Database
    DATABASE_URL: PostgresDsn
    
    # JWT
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # AI Integration
    AI_INTEGRATION_URL: str = "http://localhost:8001/api/v1/detect"
    
    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:8000"]
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    @field_validator("DATABASE_URL", mode="before")
    def assemble_db_connection(cls, v: Optional[str], info: Dict[str, Any]) -> Any:
        if isinstance(v, str):
            return v
        return PostgresDsn.build(
            scheme="postgresql+asyncpg",
            username="postgres",
            password="postgres",
            host="localhost",
            port=5432,
            path="video_surveillance",
        )
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings() 