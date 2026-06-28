# backend/app/routers/auth.py
from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm # 🔥 引入這個
from sqlmodel import Session, select

from backend.app.db.session import get_session
from backend.app.db.models import User
from backend.app.schemas import UserCreate, UserRead, Token
from backend.app.core.security import get_password_hash, verify_password, create_access_token # 🔥 引入工具
from backend.app.core.config import settings

# 建立一個路由器
router = APIRouter()

@router.post("/register", response_model=UserRead)
def register(user_in: UserCreate, session: Session = Depends(get_session)):
    """
    使用者註冊端點
    1. 接收 UserCreate (含明碼密碼)
    2. 檢查 Email 是否重複
    3. 加密密碼
    4. 存入資料庫
    5. 回傳 UserRead (不含密碼)
    """
    
    # 1. 檢查 Email 是否已經被註冊過
    # select(User).where(...) 就像 SQL 的 SELECT * FROM user WHERE email = ...
    statement = select(User).where(User.email == user_in.email)
    existing_user = session.exec(statement).first()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="這個 Email 已經被註冊過了"
        )
    
    # 2. 建立 User 物件 (將明碼轉為雜湊碼)
    new_user = User(
        email=user_in.email,
        username=user_in.username,
        hashed_password=get_password_hash(user_in.password), # 關鍵！
        is_bot=False # 預設是真人
    )
    
    # 3. 寫入資料庫
    session.add(new_user)
    session.commit()
    session.refresh(new_user) # 重新抓取資料 (為了拿到自動產生的 id 和 created_at)
    
    return new_user


# 🔥 新增登入端點
@router.post("/login", response_model=Token)
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(), # 這裡會自動接收 username & password
    session: Session = Depends(get_session)
):
    # 1. 找人：用 email 去資料庫撈使用者
    # 注意：OAuth2PasswordRequestForm 預設欄位叫 username，但我們其實是用 email 登入
    # 所以這裡我們把 form_data.username 當作 email 來用
    statement = select(User).where(User.email == form_data.username)
    user = session.exec(statement).first()
    
    # 2. 驗證：人是否存在？密碼對不對？
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    # 3. 發證：如果都對，就發一張 Token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id)}, # 我們把 User ID 藏在 Token 裡 (sub = subject)
        expires_delta=access_token_expires
    )
    
    # 4. 回傳 Token
    return {"access_token": access_token, "token_type": "bearer"}