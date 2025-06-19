# worker.py（メッセージ処理専用：Gemini API）

import os
import time
import queue
import google.generativeai as genai
from dotenv import load_dotenv
from linebot import LineBotApi
from linebot.models import TextSendMessage

load_dotenv()

line_bot_api = LineBotApi(os.getenv("LINE_CHANNEL_ACCESS_TOKEN"))
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-pro")

# 共有キュー
message_queue = queue.Queue()

# メッセージ処理ループ
def process_messages():
    while True:
        try:
            data = message_queue.get(timeout=1)
            start_time = time.time()

            # Geminiへ問い合わせ
            prompt = data["user_text"]
            response = model.generate_content(prompt)
            reply_text = response.text.strip()

            # LINEへ返信
            line_bot_api.reply_message(
                data["reply_token"],
                TextSendMessage(text=reply_text)
            )

            elapsed = round((time.time() - start_time) * 1000)
            print(f"[INFO] Replied in {elapsed}ms")

        except queue.Empty:
            continue
        except Exception as e:
            print(f"[ERROR] {e}")

# ワーカー起動（Render上では `worker: python worker.py`）
if __name__ == "__main__":
    process_messages()
