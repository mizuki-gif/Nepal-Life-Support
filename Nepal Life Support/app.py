import os
import openai
import requests
from flask import Flask, request

from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)

openai.api_key = os.getenv("OPENAI_API_KEY")
LINE_NOTIFY_TOKEN = os.getenv("LINE_NOTIFY_TOKEN")

def translate_text(text, target_lang="ja"):
    prompt = f"Translate the following text into {target_lang}:\n\n{text}"
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
    )
    return response.choices[0].message.content.strip()

def notify_staff(message):
    headers = {"Authorization": f"Bearer {LINE_NOTIFY_TOKEN}"}
    data = {"message": message}
    requests.post("https://notify-api.line.me/api/notify", headers=headers, data=data)

@app.route("/webhook", methods=['POST'])
def webhook():
    payload = request.json
    events = payload.get("events", [])
    
    for event in events:
        if event["type"] == "message" and event["message"]["type"] == "text":
            user_text = event["message"]["text"]
            translated = translate_text(user_text, target_lang="ja")
            notify_staff(f"📨 翻訳通知：\n原文: {user_text}\n翻訳: {translated}")
    return "OK"