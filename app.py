import os
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
from google.generativeai import GenerativeModel, configure
from loguru import logger
import uvicorn

# .env 読み込み
load_dotenv()

# 環境変数の取得
LINE_CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET")
LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
PORT = int(os.getenv("PORT", 10000))

# LINE Bot 初期化
line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

# Gemini 初期化
configure(api_key=GEMINI_API_KEY)
gemini_model = GenerativeModel("models/gemini-1.5-flash")

# FastAPI アプリ作成
app = FastAPI()

@app.get("/")
def health_check():
    logger.info("ヘルスチェック受信")
    return {"status": "ok"}

@app.post("/callback")
async def callback(request: Request):
    logger.info("LINE webhook受信")
    signature = request.headers.get("X-Line-Signature", "")
    body = await request.body()
    try:
        handler.handle(body.decode("utf-8"), signature)
    except InvalidSignatureError:
        return JSONResponse(status_code=400, content={"message": "Invalid signature"})
    return JSONResponse(status_code=200, content={"message": "OK"})

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event: MessageEvent):
    user_text = event.message.text
    logger.info(f"受信メッセージ: {user_text}")
    try:
        response = gemini_model.generate_content(user_text)
        reply_text = response.text.strip()
    except Exception as e:
        logger.error(f"Gemini APIエラー: {e}")
        reply_text = "エラーが発生しました。時間をおいてお試しください。"
    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply_text))

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=PORT)
