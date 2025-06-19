from loguru import logger
import time
import os
from linebot import LineBotApi
from linebot.models import TextSendMessage
from dotenv import load_dotenv
from message_queue import message_queue
from gemini_client import ask_gemini

load_dotenv()

line_bot_api = LineBotApi(os.getenv("LINE_CHANNEL_ACCESS_TOKEN"))

logger.add("worker.log", rotation="1 MB", retention="5 days", level="INFO")

def main():
    logger.info("Worker起動")
    while True:
        try:
            user_id, user_text = message_queue.get()
            logger.info(f"受信テキスト: {user_text}")
            start = time.time()

            response = ask_gemini(user_text)

            elapsed = round(time.time() - start, 2)
            logger.info(f"Gemini応答時間: {elapsed}s")

            line_bot_api.reply_message(
                user_id,
                TextSendMessage(text=response)
            )
        except Exception as e:
            logger.exception(f"エラー発生: {e}")

if __name__ == "__main__":
    main()
