from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
from openai import OpenAI
import os

app = Flask(__name__)

# กำหนดคีย์จาก environment variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
LINE_CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET")

client = OpenAI(api_key=OPENAI_API_KEY)
line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

@app.route("/callback", methods=["POST"])
def callback():
    signature = request.headers.get("X-Line-Signature", "")
    body = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return "OK"

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_text = event.message.text

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "คุณคือครูสอนเขียนโปรแกรม Python สำหรับนักเรียนมัธยม"},
            {"role": "user", "content": user_text}
        ],
        max_tokens=100
    )

    reply_text = response.choices[0].message.content.strip()
    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply_text))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
