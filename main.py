import telebot
from flask import Flask, request
import requests
import os

BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GROUP_ID = int(os.getenv("GROUP_ID"))

bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

ALLOWED_USERS = set()

# Authorize command
@bot.message_handler(commands=['auth'])
def authorize(message):
    if message.chat.id != GROUP_ID:
        bot.reply_to(message, "❌ આ બોટ ફક્ત અધિકૃત જૂથમાં જ કાર્ય કરે છે.")
        return
    ALLOWED_USERS.add(message.from_user.id)
    bot.reply_to(message, "✅ હવે તમે બોટનો ઉપયોગ કરી શકો છો!")

# Handle text
@bot.message_handler(func=lambda msg: msg.chat.id == GROUP_ID and msg.from_user.id in ALLOWED_USERS, content_types=['text'])
def handle_text(message):
    prompt = message.text
    reply = get_ai_response(prompt)
    bot.reply_to(message, reply)

# Handle photo
@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    if message.chat.id != GROUP_ID or message.from_user.id not in ALLOWED_USERS:
        bot.reply_to(message, "❌ તમે અધિકૃત નથી.")
        return

    file_id = message.photo[-1].file_id
    file_info = bot.get_file(file_id)
    file_url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_info.file_path}"

    prompt = f"Describe and solve this NEET/JEE doubt in Gujarati:\nImage URL: {file_url}"
    reply = get_ai_response(prompt)
    bot.reply_to(message, reply)

def get_ai_response(prompt):
    url = "https://api.openai.com/v1/chat/completions"
    headers = {"Authorization": f"Bearer {OPENAI_API_KEY}", "Content-Type": "application/json"}
    data = {
        "model": "gpt-4o-mini",
        "messages": [{"role": "user", "content": prompt}]
    }
    try:
        r = requests.post(url, headers=headers, json=data, timeout=30)
        res = r.json()
        return res['choices'][0]['message']['content']
    except Exception as e:
        return f"⚠️ Error: {e}"

@app.route('/' + BOT_TOKEN, methods=['POST'])
def getMessage():
    json_str = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return "!", 200

@app.route('/')
def webhook():
    bot.remove_webhook()
    bot.set_webhook(url=f"{os.getenv('RENDER_EXTERNAL_URL')}/{BOT_TOKEN}")
    return "Bot is running!", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
