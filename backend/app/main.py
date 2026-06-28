# backend/app/main.py
from contextlib import asynccontextmanager
from pathlib import Path
import uvicorn
import socket
import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles # 1. 引入靜態檔案處理
from fastapi.middleware.cors import CORSMiddleware
from backend.app.core.config import settings
from backend.app.db.session import create_db_and_tables
from backend.app.routers import auth, guilds, websockets, channels, bots, direct_messages, reactions, files, presence, threads, roles, moderation, pin_star, categories, search, notification_settings, server_templates, audit_logs, voice_chat

# 定義生命週期管理器 (Lifespan Manager)
# 這裡的邏輯是：在 yield 之前的程式碼會在伺服器啟動時執行，yield 之後的會在關閉時執行。
@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- 啟動區 (Startup) ---
    create_db_and_tables()

    # Create uploads directory if it doesn't exist
    os.makedirs("uploads", exist_ok=True)

    print("Startup: 資料庫表格檢查完成")
    print("Startup: 上傳目錄已準備就緒")
    yield
    # --- 關閉區 (Shutdown) ---
    # 如果未來有 Redis 連線要在這裡關閉，就寫在這裡
    print("Shutdown: 伺服器正在關閉...")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    lifespan=lifespan
)

# 🔥 安全的 CORS 配置
# 從環境變數讀取允許的來源
allowed_origins_str = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://localhost:8000")
ALLOWED_ORIGINS = [origin.strip() for origin in allowed_origins_str.split(",")] if allowed_origins_str else []

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# prefix="/auth" 代表這個檔案裡的所有 API 都會以 /auth 開頭
# tags=["Auth"] 會在 Swagger UI 上把它們歸類在 Auth 區塊
app.include_router(auth.router, prefix="/auth", tags=["Auth"])
# 注意：我們加上了 /api 前綴，所以完整網址是 POST /api/guilds
app.include_router(guilds.router, prefix="/api/guilds", tags=["Guilds"])
app.include_router(channels.router, prefix="/api/channels", tags=["Channels"])
app.include_router(bots.router, prefix="/api/bots", tags=["Bots"]) # 🔥 掛載
# 注意：WebSocket 通常不加 /api 前綴，為了區分 HTTP 和 WS
app.include_router(websockets.router, prefix="/ws", tags=["WebSockets"])

# Direct Messages API
app.include_router(direct_messages.router, prefix="/api/dms", tags=["Direct Messages"])

# Reactions API
app.include_router(reactions.router, prefix="/api/reactions", tags=["Reactions"])

# File Upload API
app.include_router(files.router, prefix="/api/files", tags=["Files"])

# Presence API
app.include_router(presence.router, prefix="/api/presence", tags=["Presence"])

# Threads API
app.include_router(threads.router, prefix="/api/threads", tags=["Threads"])

# Roles and Permissions API
app.include_router(roles.router, prefix="/api/roles", tags=["Roles"])

# Moderation API
app.include_router(moderation.router, prefix="/api/moderation", tags=["Moderation"])

# Pinning and Starring API
app.include_router(pin_star.router, prefix="/api/pin-star", tags=["PinStar"])

# Categories API
app.include_router(categories.router, prefix="/api/categories", tags=["Categories"])

# Search API
app.include_router(search.router, prefix="/api/search", tags=["Search"])

# Notification Settings API
app.include_router(notification_settings.router, prefix="/api/notifications", tags=["Notifications"])

# Server Templates API
app.include_router(server_templates.router, prefix="/api/templates", tags=["Templates"])

# Audit Logs API
app.include_router(audit_logs.router, prefix="/api/audit-logs", tags=["AuditLogs"])

# Voice Chat API
app.include_router(voice_chat.router, prefix="/api/voice", tags=["Voice"])

# 測試用 API 改名，避免佔用根目錄 "/"
@app.get("/api/health")
def health_check():
    return {"status": "ok", "message": "Discord Clone API Online"}

# --- 🔥 關鍵：掛載前端靜態檔案 ---
# 這樣做之後，訪問 http://localhost:PORT/ 就會看到 index.html
# 訪問 http://localhost:PORT/login.html 就會看到登入頁
# 我們使用 Path 來確保路徑正確 (假設你在專案根目錄執行)
BASE_DIR = Path(__file__).resolve().parent.parent.parent # 指向 discord-clone 根目錄
FRONTEND_DIR = BASE_DIR / "frontend"

app.mount("/", StaticFiles(directory=str(FRONTEND_DIR), html=True), name="static")

# =========================
# 自動找可用 port
# =========================
def find_free_port(start: int = 8000, end: int = 8100) -> int:
    """
    從 start 掃到 end-1
    找到第一個可 bind 的 port 就回傳
    """
    for port in range(start, end):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                # bind 成功代表這個 port 空著
                s.bind(("0.0.0.0", port))
                return port
            except OSError:
                # 被佔用就跳過
                continue

    raise RuntimeError(f"No free port available in range {start}-{end-1}")


# =========================
# 用 Python 方式啟動 Uvicorn（才做得到自動換 port）
# =========================
if __name__ == "__main__":
    port = find_free_port()
    print(f"🚀 Server starting on http://localhost:{port}")
    uvicorn.run(
        "backend.app.main:app",   # ✅ 用 import string，reload 才能用
        host="0.0.0.0",
        port=port,
        reload=True,  # 開發用：改 code 會自動重載
    )