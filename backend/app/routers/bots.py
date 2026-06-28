# backend/app/routers/bots.py
import secrets
import json
from typing import List, Optional
from pydantic import BaseModel 
from fastapi import APIRouter, Depends, HTTPException, Header
from sqlmodel import Session, select

from backend.app.db.session import get_session
from backend.app.db.models import Bot, User, Message
from backend.app.schemas import BotCreate, BotReadWithToken, BotRead
from backend.app.deps import get_current_user
from backend.app.websockets.manager import manager # 引入 WebSocket 管理器來廣播

router = APIRouter()

# 1. 創建機器人 (開發者後台)
@router.post("/", response_model=BotReadWithToken)
def create_bot(
    bot_in: BotCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    # A. 建立 Bot 的 User 帳號 (隨機密碼，因為 Bot 不用密碼登入)
    bot_user = User(
        email=f"bot_{secrets.token_hex(4)}@discord.clone", # 假 Email
        username=bot_in.name,
        hashed_password=secrets.token_urlsafe(20), # 隨機密碼
        is_bot=True,
        avatar_url=None
    )
    session.add(bot_user)
    session.commit()
    session.refresh(bot_user)

    # B. 生成 Bot Token (類似 Discord 的做法)
    bot_token = secrets.token_urlsafe(32)

    # C. 建立 Bot 紀錄
    new_bot = Bot(
        name=bot_in.name,
        token=bot_token,
        bot_user_id=bot_user.id, # type: ignore
        owner_id=current_user.id # type: ignore
    )
    session.add(new_bot)
    session.commit()
    session.refresh(new_bot)

    # 回傳包含 Token 的資訊
    return BotReadWithToken(
        id=new_bot.id, # type: ignore
        name=new_bot.name,
        bot_user_id=new_bot.bot_user_id,
        created_at=new_bot.created_at,
        token=new_bot.token
    )

# 2. 獲取我的機器人列表
@router.get("/", response_model=List[BotRead])
def read_my_bots(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    return current_user.my_bots

# 3. 🔥 Bot 發送訊息 API (HTTP POST)
# 這就是讓外部 Python 腳本呼叫的接口
class BotMessage(BaseModel):
    content: str

@router.post("/channels/{channel_id}/messages")
async def bot_send_message(
    channel_id: int,
    message: BotMessage,
    # 使用 Header 來驗證 Bot Token (Authorization: Bot <token>)
    authorization: str = Header(None), 
    session: Session = Depends(get_session)
):
    # A. 驗證 Token 格式
    if not authorization or not authorization.startswith("Bot "):
        raise HTTPException(status_code=401, detail="Invalid authorization header. Use 'Bot <token>'")
    
    token = authorization.split(" ")[1]
    
    # B. 找 Bot
    statement = select(Bot).where(Bot.token == token)
    bot = session.exec(statement).first()
    
    if not bot:
        raise HTTPException(status_code=401, detail="Invalid Bot Token")
        
    # C. 寫入訊息
    # 這裡的 user_id 使用 Bot 對應的 bot_user_id
    # 注意：這裡應該要檢查 bot 有沒有權限在這個 channel 發言，暫時跳過
    
    bot_user = session.get(User, bot.bot_user_id)
    
    new_message = Message(
        content=message.content,
        user_id=bot_user.id, # type: ignore
        channel_id=channel_id
    )
    session.add(new_message)
    session.commit()
    session.refresh(new_message)
    
    # D. 🔥 透過 WebSocket 廣播給前端 (這樣網頁上才會跳出來)
    message_payload = {
        "id": new_message.id,
        "content": new_message.content,
        "user_id": bot_user.id, # type: ignore
        "username": bot_user.username, # type: ignore
        "avatar_url": bot_user.avatar_url, # type: ignore
        "is_bot": True, # 🔥 這裡直接寫死 True，因為這是 Bot API
        "created_at": new_message.created_at.isoformat()
    }
    
    await manager.broadcast(json.dumps(message_payload), channel_id)
    
    return {"status": "sent", "message_id": new_message.id}

class BotUpdate(BaseModel):
    name: Optional[str] = None
    avatar_url: Optional[str] = None

# 4. 更新機器人資訊 (改名、改頭像)
@router.put("/{bot_id}", response_model=BotRead)
def update_bot(
    bot_id: int,
    bot_update: BotUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    bot = session.get(Bot, bot_id)
    if not bot or bot.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Bot not found or permission denied")

    # 更新 Bot 表
    if bot_update.name:
        bot.name = bot_update.name
    
    # 同步更新底層 User 表 (這樣聊天室才會變)
    bot_user = session.get(User, bot.bot_user_id)
    if bot_user:
        if bot_update.name:
            bot_user.username = bot_update.name
        if bot_update.avatar_url is not None:
            bot_user.avatar_url = bot_update.avatar_url
        session.add(bot_user)

    session.add(bot)
    session.commit()
    session.refresh(bot)
    return bot

# 5. 重設 Token (Regenerate Token)
@router.post("/{bot_id}/token", response_model=BotReadWithToken)
def regenerate_token(
    bot_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    bot = session.get(Bot, bot_id)
    if not bot or bot.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Bot not found")

    # 產生新 Token
    new_token = secrets.token_urlsafe(32)
    bot.token = new_token
    
    session.add(bot)
    session.commit()
    session.refresh(bot)
    
    return bot

# 6. 刪除機器人
@router.delete("/{bot_id}")
def delete_bot(
    bot_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    bot = session.get(Bot, bot_id)
    if not bot or bot.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Bot not found")
        
    # 這裡我們只刪除 Bot 關聯，通常 bot_user 可以留著當歷史紀錄，或者也一起刪除
    # 簡單起見，我們刪除 Bot 紀錄
    session.delete(bot)
    session.commit()
    return {"ok": True}