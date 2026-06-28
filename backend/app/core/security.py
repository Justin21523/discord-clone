# backend/app/core/security.py
from datetime import datetime, timedelta
from typing import Optional
from jose import jwt # 我們剛安裝的 python-jose 套件
from passlib.context import CryptContext
from backend.app.core.config import settings

# 設定加密演算法為 bcrypt (目前業界標準)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """ 驗證密碼是否正確 (登入用) """
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """ 將明碼加密成亂碼 (註冊用) """
    return pwd_context.hash(password)

# 🔥 建立存取權杖 (Create Access Token)
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    
    # 設定過期時間
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
        
    # 將過期時間寫入 Token 資料中
    to_encode.update({"exp": expire})
    
    # 使用我們的 SECRET_KEY 進行簽章 (Sign)
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt