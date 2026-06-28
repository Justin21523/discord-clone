# backend/app/deps.py

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlmodel import Session

from backend.app.core.config import settings
from backend.app.db.session import get_session
from backend.app.db.models import User

# 1. 定義 OAuth2 方案
# 這告訴 FastAPI：如果要拿 Token，請去 /auth/login 這個網址找
# 這會讓 Swagger UI 右上角出現 "Authorize" 鎖頭按鈕
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")
# 注意：因為我們還沒設定 API_V1_STR 的路由前綴，暫時指到 /auth/login 即可
# 但為了簡單，這裡我們先寫死 tokenUrl="/auth/login"
oauth2_scheme_simple = OAuth2PasswordBearer(tokenUrl="/auth/login")

# 2. 核心函式：取得當前使用者
async def get_current_user(
    token: str = Depends(oauth2_scheme_simple),
    session: Session = Depends(get_session)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # A. 解密 Token
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub") # type: ignore 記得我們在 auth.py 裡把 user.id 放在 "sub" 欄位嗎？
        
        if user_id is None:
            raise credentials_exception
            
    except JWTError:
        raise credentials_exception
        
    # B. 去資料庫找人
    user = session.get(User, int(user_id))
    
    if user is None:
        raise credentials_exception
        
    return user