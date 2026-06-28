# backend/app/core/config.py
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings:
    PROJECT_NAME: str = "Discord Clone API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    # 資料庫位置 (使用 SQLite)
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./discord.db")
    # 🔥 新增 JWT 設定
    # 這串亂碼非常重要，絕對不能外洩！它是用來驗證 Token 真偽的印章
    SECRET_KEY: str = os.getenv("SECRET_KEY")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))  # Token 30 分鐘後過期

    def __init__(self):
        # Ensure SECRET_KEY is set
        if not self.SECRET_KEY:
            raise ValueError("SECRET_KEY environment variable must be set")

settings = Settings()