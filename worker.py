import os
import time
from dotenv import load_dotenv
from linebot import LineBotApi
from linebot.models import TextSendMessage
from openai import OpenAI
from queue_store import event_queue

# 環境変数
load_dotenv()
LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
openai_client = OpenAI(api_key=OPENAI_API_KEY)

def run_worker():
    while True:
        event = event_queue.get()
        start_time = time.time()
        user_text = event.message.text
        user_id = event.source.user_id

        print(f"🧠 OpenAI処理開始: {user_text}")

        try:
            response = openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "以下の文章の意味をやさしく説明してください。"},
                    {"role": "user", "content": user_text}
                ],
                max_tokens=100
            )
            reply_text = response.choices[0].message.content.strip()
        except Exception as e:
            reply_text = f"OpenAIエラー: {str(e)}"

        try:
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=reply_text)
            )
            elapsed = round((time.time() - start_time) * 1000, 2)
            print(f"✅ LINE返信完了 in {elapsed}ms: {reply_text}")
        except Exception as e:
            print("❌ LINE送信エラー:", e)

if __name__ == "__main__":
    print("🚀 Worker起動中...")
    run_worker()
