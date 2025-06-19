from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage
from dotenv import load_dotenv
import os
from message_queue import message_queue
import uvicorn

from loguru import logger

load_dotenv()

app = FastAPI()

line_bot_api = LineBotApi(os.getenv("LINE_CHANNEL_ACCESS_TOKEN"))
handler = WebhookHandler(os.getenv("LINE_CHANNEL_SECRET"))

logger.add("app.log", rotation="500 KB")

@app.get("/")
def health_check():
    logger.info("ヘルスチェック受信")
    return {"status": "ok"}
    
@app.post("/callback")
async def callback(request: Request):
    signature = request.headers.get("X-Line-Signature")
    body = await request.body()
    body_text = body.decode("utf-8")
    logger.info("LINE webhook受信")

    try:
        handler.handle(body_text, signature)
    except InvalidSignatureError:
        raise HTTPException(status_code=400, detail="Invalid signature")
    return "OK"

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_text = event.message.text
    user_id = event.source.user_id
    message_queue.put((user_id, user_text))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=10000)  # ポート明示でRender対応
