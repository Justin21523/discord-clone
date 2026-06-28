# my_smart_bot.py
import asyncio
from bot_framework import BotClient
import datetime

# --- 設定區 ---
# 請去 Developer Portal 複製你的 Token
BOT_TOKEN = "lQVoQLDJxZjoDXpXaEkIrlandU1Clnj8fiOZlR1sWlQ" 
CHANNEL_ID = 1 # 你想讓 Bot 進入的頻道 ID
# --------------

class MySmartBot(BotClient):
    async def on_message(self, message):
        # 1. 基本資訊解析
        sender = message.get("username")
        content = message.get("content", "")
        is_bot = message.get("is_bot", False)

        # 2. 重要：絕對不要回覆機器人自己 (避免無限迴圈)
        if is_bot:
            return

        print(f"👂 聽到 {sender} 說: {content}")

        # 3. 邏輯判斷區
        if content == "!hello":
            await self.send_message(f"你好啊 {sender}！我是智慧機器人 🤖")
        
        elif content == "!time":
            now = datetime.datetime.now().strftime("%H:%M:%S")
            await self.send_message(f"現在時間是: {now}")
            
        elif "笨蛋" in content:
            await self.send_message("請注意禮貌喔！😡")

    async def background_loop(self):
        """ 背景任務：每 30 秒自動報時 """
        print("⏰ 背景計時器已啟動")
        while self.running:
            await asyncio.sleep(30) # 等待 30 秒
            # await self.send_message("💡 貼心提醒：記得喝水喔！(自動排程訊息)")

# 執行 Bot
if __name__ == "__main__":
    # 需要先確認 Port
    port = input("請輸入後端 Port (例如 59268): ").strip()
    
    client = MySmartBot(BOT_TOKEN, api_base_url=f"http://localhost:{port}")
    
    try:
        asyncio.run(client.start(CHANNEL_ID))
    except KeyboardInterrupt:
        print("機器人已關閉")