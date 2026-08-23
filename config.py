"""Configuration management for FastAPI + RayMine"""

from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    """Application settings with validation"""
    
    # OpenAI Configuration (REQUIRED)
    openai_api_key: str
    openai_model: str = "gpt-4"
    openai_temperature: float = 0.7
    openai_max_tokens: int = 2048
    
    # Supabase Configuration (REQUIRED)
    supabase_url: str
    supabase_key: str
    
    # RayMine Configuration
    raymine_env: str = "development"
    log_level: str = "INFO"
    raymine_memory_table: str = "memories"
    raymine_vector_enabled: bool = True
    raymine_memory_limit: int = 10  # Max conversation history
    raymine_context_ranking: bool = True  # Enable context ranking
    raymine_conflict_resolution: bool = True  # Enable conflict resolution
    
    # FastAPI Configuration
    fastapi_host: str = "0.0.0.0"
    fastapi_port: int = 8000
    fastapi_reload: bool = True
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
    
    def validate_required_vars(self) -> dict:
        """Validate all required environment variables"""
        errors = {}
        
        # Check OpenAI
        if not self.openai_api_key or self.openai_api_key == "sk-proj-your-key-here":
            errors["OPENAI_API_KEY"] = "Missing or invalid OpenAI API key"
        
        if not self.openai_api_key.startswith("sk-"):
            errors["OPENAI_API_KEY"] = "Invalid OpenAI API key format"
        
        # Check Supabase
        if not self.supabase_url or "supabase.co" not in self.supabase_url:
            errors["SUPABASE_URL"] = "Missing or invalid Supabase URL"
        
        if not self.supabase_key:
            errors["SUPABASE_KEY"] = "Missing Supabase API key"
        
        return errors


# Global settings instance
try:
    settings = Settings()
    validation_errors = settings.validate_required_vars()
    
    if validation_errors:
        print("\n⚠️  CONFIGURATION ERRORS:")
        for key, error in validation_errors.items():
            print(f"  - {key}: {error}")
        print("\n📝 Please create .env file with proper credentials")
        print("   Copy from .env.example and fill in actual values\n")
        
        # Exit if in production
        if os.getenv("RAYMINE_ENV") == "production":
            raise ValueError("Missing required environment variables in production")
    else:
        print("✅ Configuration loaded successfully")
        
except Exception as e:
    print(f"❌ Configuration error: {str(e)}")
    raise
