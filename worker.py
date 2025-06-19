import time
from dotenv import load_dotenv
from linebot import LineBotApi
from linebot.models import TextSendMessage
import os

from message_queue import message_queue
from gemini_client import ask_gemini

load_dotenv()
line_bot_api = LineBotApi(os.getenv("LINE_CHANNEL_ACCESS_TOKEN"))

def run_worker():
    print("🚀 Gemini Worker 起動中...")
    while True:
        event = message_queue.get()
        user_text = event.message.text
        reply_text = ask_gemini(user_text)

        try:
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=reply_text)
            )
        except Exception as e:
            print(f"❌ LINE送信エラー: {e}")

        time.sleep(1)
