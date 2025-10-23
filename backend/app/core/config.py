"""应用配置"""
from typing import List
from pydantic_settings import BaseSettings
from pydantic import validator
import os


class Settings(BaseSettings):
    """应用配置类"""
    
    # 基础配置
    APP_NAME: str = "AI有声书工具"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    SECRET_KEY: str = "your-secret-key-change-in-production"
    
    # 数据库配置
    DATABASE_URL: str = "mysql+pymysql://root:password@localhost:3306/asr_story"
    DATABASE_POOL_SIZE: int = 10
    DATABASE_MAX_OVERFLOW: int = 20
    
    # CORS配置（局域网访问）
    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
    ]
    
    @validator("CORS_ORIGINS", pre=True)
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v
    
    # 文件存储配置
    STORAGE_PATH: str = "./storage"
    MAX_UPLOAD_SIZE: int = 104857600  # 100MB
    
    # TTS配置（预留）
    TTS_DEFAULT_ENGINE: str = "azure"
    TTS_AZURE_KEY: str = ""
    TTS_AZURE_REGION: str = ""
    TTS_ALIYUN_APPKEY: str = ""
    TTS_ALIYUN_ACCESS_KEY: str = ""
    TTS_TENCENT_SECRET_ID: str = ""
    TTS_TENCENT_SECRET_KEY: str = ""
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# 全局配置实例
settings = Settings()

# 确保存储目录存在
os.makedirs(os.path.join(settings.STORAGE_PATH, "uploads"), exist_ok=True)
os.makedirs(os.path.join(settings.STORAGE_PATH, "audio"), exist_ok=True)
os.makedirs(os.path.join(settings.STORAGE_PATH, "temp"), exist_ok=True)

