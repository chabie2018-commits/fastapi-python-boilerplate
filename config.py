"""Configuration management for FastAPI + RayMine"""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings"""
    
    # OpenAI Configuration
    openai_api_key: str
    openai_model: str = "gpt-4"
    openai_temperature: float = 0.7
    openai_max_tokens: int = 2048
    
    # Supabase Configuration
    supabase_url: str
    supabase_key: str
    
    # RayMine Configuration
    raymine_env: str = "development"
    log_level: str = "INFO"
    raymine_memory_table: str = "memories"
    raymine_vector_enabled: bool = True
    
    # FastAPI Configuration
    fastapi_host: str = "0.0.0.0"
    fastapi_port: int = 8000
    fastapi_reload: bool = True
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global settings instance
settings = Settings()
