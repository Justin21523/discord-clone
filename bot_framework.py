# bot_framework.py
import asyncio
import websockets
import json
import requests
import time

class BotClient:
    def __init__(self, token, api_base_url="http://localhost:8000"):
        self.token = token
        self.api_base_url = api_base_url
        self.user_info = None
        self.running = False

    async def start(self, channel_id):
        """ 啟動機器人並開始監聽指定頻道 """
        self.channel_id = channel_id
        # 自動切換 ws/wss
        ws_url = self.api_base_url.replace("http", "ws").replace("https", "wss")
        uri = f"{ws_url}/ws/{channel_id}?token={self.token}"

        print(f"🤖 Bot 正在連線到頻道 {channel_id}...")
        
        async with websockets.connect(uri) as websocket:
            print("✅ Gateway 連線成功！開始監聽事件...")
            self.running = True
            
            # 啟動背景任務 (例如定時發送)
            asyncio.create_task(self.background_loop())

            try:
                while self.running:
                    message = await websocket.recv()
                    data = json.loads(message)
                    
                    # 觸發事件處理
                    await self.on_message(data)
            except websockets.exceptions.ConnectionClosed:
                print("❌ 連線已中斷")

    async def on_message(self, message):
        """ 當收到訊息時觸發 (開發者可覆寫此函式) """
        print(f"收到訊息: {message}")

    async def send_message(self, content):
        """ 主動發送訊息到當前頻道 """
        url = f"{self.api_base_url}/api/bots/channels/{self.channel_id}/messages"
        headers = {"Authorization": f"Bot {self.token}"}
        
        # 使用 run_in_executor 來在 async 函式中執行同步的 requests
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, lambda: requests.post(url, json={"content": content}, headers=headers))
        print(f"📤 已發送回覆: {content}")

    async def background_loop(self):
        """ 背景任務迴圈 (開發者可覆寫) """
        pass