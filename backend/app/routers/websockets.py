# backend/app/routers/websockets.py
import json
from datetime import datetime
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query, Depends
from sqlmodel import Session, select
from jose import jwt, JWTError

from backend.app.websockets.manager import manager
from backend.app.core.config import settings
from backend.app.db.session import get_session
from backend.app.db.models import User, Message, Bot
from backend.app.services.message_service import MessageService

router = APIRouter()

# 🔥 修改：支援 User Token 與 Bot Token
async def authenticate_connection(
    token: str,
    session: Session
) -> User | None:
    # 1. 嘗試當作 User Token 解析 (JWT)
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id = payload.get("sub")
        if user_id:
            return session.get(User, int(user_id))
    except JWTError:
        pass # 解析失敗，可能是 Bot Token，繼續往下試
        
    # 2. 嘗試當作 Bot Token 解析 (直接查 DB)
    # Bot Token 不是 JWT，是我們生成的隨機字串
    statement = select(Bot).where(Bot.token == token)
    bot = session.exec(statement).first()
    
    if bot:
        # 如果是 Bot，我們回傳它對應的 User 帳號
        return session.get(User, bot.bot_user_id)
        
    return None

# 🔥 WebSocket 端點
# 網址格式: ws://localhost:8000/ws/{channel_id}?token=eyJ...
@router.websocket("/{channel_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    channel_id: int,
    token: str = Query(...), # 必填參數
    session: Session = Depends(get_session)
):
    # 1. 驗證身分 (Handshake 階段)
    user = await authenticate_connection(token, session)
    if user is None:
        # 如果 Token 無效，直接拒絕連線 (關閉代碼 1008 Policy Violation)
        await websocket.close(code=1008)
        return

    # 2. 建立連線
    await manager.connect(websocket, channel_id, user.id)

    try:
        # 3. 監聽迴圈 (Listening Loop)
        while True:
            # 等待前端傳送訊息...
            data = await websocket.receive_text()

            # Check rate limiting
            if manager.is_rate_limited(websocket):
                # Send rate limit warning to the user
                try:
                    await websocket.send_text(json.dumps({
                        "error": "Rate limit exceeded. Please slow down your messages."
                    }))
                except:
                    pass  # Ignore errors when sending rate limit warning
                continue  # Skip processing this message

            # 1.🔥 使用服務層創建訊息
            # Parse JSON data to check if it contains thread information
            import json
            try:
                parsed_data = json.loads(data)
                if isinstance(parsed_data, dict) and 'content' in parsed_data:
                    content = parsed_data['content']
                    replied_to_id = parsed_data.get('replied_to_id')
                else:
                    # If not a structured message, treat as plain text
                    content = data
                    replied_to_id = None
            except json.JSONDecodeError:
                # If not valid JSON, treat as plain text
                content = data
                replied_to_id = None

            new_message = MessageService.create_message(
                session=session,
                content=content,
                user_id=user.id, # type: ignore
                channel_id=channel_id,
                replied_to_id=replied_to_id
            )

            # 2. 🔥 組裝 JSON 廣播封包
            # 這樣前端拿到的是一個結構化的物件，而不是純文字
            message_payload = {
                "id": new_message.id,
                "content": new_message.content,
                "user_id": user.id,
                "username": user.username,
                "avatar_url": user.avatar_url,
                "is_bot": user.is_bot, # 🔥 新增這行 (真人通常是 False)
                "created_at": new_message.created_at.isoformat()
            }

            # 透過 Manager 廣播 JSON 字串
            await manager.broadcast(json.dumps(message_payload), channel_id)

    except WebSocketDisconnect:
        # 4. 斷線處理
        manager.disconnect(websocket, channel_id)
        # 可選擇性廣播：某某人離開了
        await manager.broadcast(json.dumps({
            "system": True,
            "message": f"{user.username} left the chat.",
            "timestamp": datetime.now().isoformat()
        }), channel_id)