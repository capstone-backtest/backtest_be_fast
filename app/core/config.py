"""
API 서버 설정 관리
"""
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """애플리케이션 설정"""
    
    # API 설정
    api_v1_str: str = "/api/v1"
    project_name: str = "Backtesting API Server"
    version: str = "1.0.0"
    description: str = "FastAPI server for backtesting.py library"
    
    # 서버 설정
    host: str = Field(default="0.0.0.0", env="HOST")
    port: int = Field(default=8000, env="PORT")
    debug: bool = Field(default=False, env="DEBUG")
    
    # CORS 설정
    backend_cors_origins: list[str] = [
        "http://localhost:3000",
        "http://localhost:8000",
        "http://localhost:8080",
    ]
    
    # 백테스팅 설정
    default_initial_cash: float = 10000.0
    max_backtest_duration_days: int = 3650  # 10년
    default_commission: float = 0.002  # 0.2%
    
    # 데이터 설정
    data_cache_dir: str = "data_cache"
    max_cache_age_hours: int = 24
    
    # 최적화 설정
    max_optimization_iterations: int = 1000
    optimization_timeout_seconds: int = 300  # 5분
    
    # 로깅 설정
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    
    # 보안 설정
    secret_key: str = Field(default="your-secret-key-here", env="SECRET_KEY")
    
    # 외부 API 설정
    yahoo_finance_timeout: int = 30
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# 글로벌 설정 인스턴스
settings = Settings() 