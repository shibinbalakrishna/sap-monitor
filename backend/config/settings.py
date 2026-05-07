#!/usr/bin/env python3
"""
Configuration settings for SAP Infrastructure Monitoring Platform.
"""

from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    """
    
    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/sap_monitor"
    DATABASE_ECHO: bool = False
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 10
    
    # FastAPI
    FAST_API_HOST: str = "0.0.0.0"
    FAST_API_PORT: int = 8000
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"
    
    # Security
    SECRET_KEY: str = "your-super-secret-key-change-this-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_HOURS: int = 24
    
    # SSH Monitoring
    SSH_TIMEOUT: int = 10
    SSH_RETRIES: int = 3
    SSH_PARALLEL_WORKERS: int = 10
    SSH_PORT: int = 22
    
    # Ollama AI
    OLLAMA_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama2"
    OLLAMA_TEMPERATURE: float = 0.7
    OLLAMA_TIMEOUT: int = 30
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_EXPIRE_TIME: int = 3600
    
    # Scheduler
    SCHEDULER_INTERVAL_SECONDS: int = 60
    SCHEDULER_MAX_INSTANCES: int = 1
    
    # Alerts
    ALERT_EMAIL_ENABLED: bool = False
    ALERT_EMAIL_SMTP_SERVER: Optional[str] = None
    ALERT_EMAIL_SMTP_PORT: int = 587
    ALERT_EMAIL_FROM: Optional[str] = None
    ALERT_TEAMS_WEBHOOK_URL: Optional[str] = None
    ALERT_SLACK_WEBHOOK_URL: Optional[str] = None
    
    # Data Retention
    METRIC_RETENTION_DAYS: int = 30
    AUDIT_LOG_RETENTION_DAYS: int = 90
    
    # API Rate Limiting
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_PERIOD: int = 60
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Create settings instance
settings = Settings()
