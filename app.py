from fastapi import FastAPI, Request
from loguru import logger
from linebot import LineBotApi, WebhookHandler
from linebot.models import MessageEvent, TextMessage, TextSendMessage
from linebot.exceptions import InvalidSignatureError
from google.generativeai import configure, GenerativeModel
import os
from dotenv import load_dotenv

# 環境変数の読み込み
load_dotenv()

app = FastAPI()

# LINE Bot設定
line_bot_api = LineBotApi(os.getenv("LINE_CHANNEL_ACCESS_TOKEN"))
handler = WebhookHandler(os.getenv("LINE_CHANNEL_SECRET"))

# Gemini設定
configure(api_key=os.getenv("GEMINI_API_KEY"))
model = GenerativeModel("models/gemini-pro")

@app.get("/")
def health_check():
    logger.info("ヘルスチェック受信")
    return {"status": "ok"}

@app.post("/callback")
async def callback(request: Request):
    signature = request.headers.get("X-Line-Signature", "")
    body = await request.body()
    body_text = body.decode("utf-8")

    logger.info("LINE webhook受信")

    try:
        handler.handle(body_text, signature)
    except InvalidSignatureError:
        logger.error("署名検証失敗")
        return "Invalid signature", 400

    return "OK"

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_message = event.message.text
    logger.info(f"受信メッセージ: {user_message}")

    try:
        response = model.generate_content(user_message)
        reply_text = response.text.strip()
    except Exception as e:
        logger.error(f"Gemini APIエラー: {e}")
        reply_text = "エラーが発生しました。後ほどお試しください。"

    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=reply_text)
    )

# uvicorn経由で起動（Render用）
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
