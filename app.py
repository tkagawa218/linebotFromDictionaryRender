import os
import threading
from flask import Flask, request, abort
from dotenv import load_dotenv

from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

import openai

# 環境変数の読み込み（ローカル実行時のみ有効、Renderでは無視される）
load_dotenv()

# APIキーの取得
LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
LINE_CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Flaskアプリケーション作成
app = Flask(__name__)

# LINE SDK設定
line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

# OpenAIキー設定
openai.api_key = OPENAI_API_KEY

# GET / にアクセスがあった場合のレスポンス（Renderのヘルスチェック対策）
@app.route("/", methods=["GET"])
def index():
    return "LINE Bot is running.", 200

# Webhookエンドポイント
@app.route("/callback", methods=["POST"])
def callback():
    signature = request.headers["X-Line-Signature"]
    body = request.get_data(as_text=True)
    print("🔔 Webhook Received:", body)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        print("❌ InvalidSignatureError: 署名が一致しません")
        abort(400)

    return "OK"

# ユーザーのメッセージを処理（非同期でOpenAI処理を開始）
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    threading.Thread(target=process_openai_reply, args=(event,)).start()

# OpenAIとの連携と返信処理
def process_openai_reply(event):
    user_text = event.message.text
    print(f"📝 User: {user_text}")

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "以下の文章の意味をやさしく説明してください。"},
                {"role": "user", "content": user_text}
            ],
            max_tokens=100
        )
        reply_text = response.choices[0].message.content.strip()
        print("🤖 ChatGPT Response:", reply_text)
    except Exception as e:
        reply_text = f"エラーが発生しました: {str(e)}"
        print("❌ OpenAI Error:", e)

    try:
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=reply_text)
        )
        print("✅ LINE返信成功")
    except Exception as e:
        print("❌ LINEへの返信エラー:", e)

# ポート指定（Renderでの起動に必須）
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
