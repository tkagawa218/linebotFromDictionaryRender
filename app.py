import os
import threading
from flask import Flask, request, abort
from dotenv import load_dotenv

from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

from openai import OpenAI

# 環境変数の読み込み（ローカル用）
load_dotenv()

# 各種APIキー
LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
LINE_CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Flaskアプリケーション
app = Flask(__name__)

# LINE Bot設定
line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

# OpenAIクライアント（v1.0+対応）
openai_client = OpenAI(api_key=OPENAI_API_KEY)

# Renderなどのヘルスチェック対応
@app.route("/", methods=["GET"])
def index():
    return "LINE Bot is running.", 200

# LINE Webhookの受け口
@app.route("/callback", methods=["POST"])
def callback():
    signature = request.headers["X-Line-Signature"]
    body = request.get_data(as_text=True)
    print("🔔 Webhook Received:", body)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        print("❌ InvalidSignatureError: チャネルシークレットが一致しません")
        abort(400)

    return "OK"

# ユーザーからのメッセージを処理（OpenAI連携は非同期で行う）
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    threading.Thread(target=process_openai_reply, args=(event,)).start()

# OpenAIに問い合わせてLINEに返信
def process_openai_reply(event):
    user_text = event.message.text
    print("📝 User message:", user_text)

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
        print("🤖 OpenAI reply:", reply_text)
    except Exception as e:
        reply_text = f"OpenAI APIエラー: {str(e)}"
        print("❌ OpenAI Error:", e)

    try:
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=reply_text)
        )
        print("✅ LINEへの返信成功")
    except Exception as e:
        print("❌ LINEへの返信エラー:", e)

# アプリ起動設定（Render用）
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
