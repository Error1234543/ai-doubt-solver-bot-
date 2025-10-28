import os
from flask import Flask, request
import telebot
import openai

# ==============================
# 🔧 CONFIG
# ==============================
BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ALLOWED_GROUP_ID = -1001234567890  # 👈 apna group ID daalna
OWNER_ID = 8226637107
AUTHORIZED_USERS = {8226637107}

if not BOT_TOKEN:
    raise ValueError("❌ BOT_TOKEN missing! Set it in Render Environment Variables.")
if not OPENAI_API_KEY:
    raise ValueError("❌ OPENAI_API_KEY missing!")

openai.api_key = OPENAI_API_KEY
bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

# ==============================
# 🔒 AUTH SYSTEM
# ==============================
@bot.message_handler(commands=['auth'])
def authorize_user(message):
    if message.from_user.id != OWNER_ID:
        bot.reply_to(message, "❌ Sirf owner hi access de sakta hai.")
        return
    try:
        user_id = int(message.text.split()[1])
        AUTHORIZED_USERS.add(user_id)
        bot.reply_to(message, f"✅ Access granted to {user_id}")
    except:
        bot.reply_to(message, "❌ Format: /auth <user_id>")

# ==============================
# 🧠 AI SOLVER
# ==============================
def ask_ai(prompt):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "તમે NEET/JEE ના પ્રશ્નો માટે ગુજરાતી માં સમજ આપતો AI છો."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=600
        )
        return response.choices[0].message['content']
    except Exception as e:
        return f"⚠️ Error: {e}"

# ==============================
# 📸 IMAGE DOUBT HANDLER
# ==============================
@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    if message.chat.id != ALLOWED_GROUP_ID:
        return
    if message.from_user.id not in AUTHORIZED_USERS:
        bot.reply_to(message, "❌ Access denied. Contact owner.")
        return
    bot.reply_to(message, "🧠 Analyzing image... (please wait)")
    try:
        file_info = bot.get_file(message.photo[-1].file_id)
        file_url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_info.file_path}"
        prompt = f"Explain this NEET/JEE question in Gujarati:\nImage URL: {file_url}"
        ai_response = ask_ai(prompt)
        bot.reply_to(message, ai_response)
    except Exception as e:
        bot.reply_to(message, f"⚠️ Image processing error: {e}")

# ==============================
# ✍️ TEXT DOUBT HANDLER
# ==============================
@bot.message_handler(func=lambda m: True)
def handle_text(message):
    if message.chat.id != ALLOWED_GROUP_ID:
        return
    if message.from_user.id not in AUTHORIZED_USERS:
        bot.reply_to(message, "❌ Access denied. Contact owner.")
        return
    ai_reply = ask_ai(message.text)
    bot.reply_to(message, ai_reply)

# ==============================
# 🌐 FLASK SERVER FOR RENDER
# ==============================
@app.route('/')
def home():
    return "🤖 AI Doubt Solver Bot (@batmandmbot) Running!"

@app.route(f'/{BOT_TOKEN}', methods=['POST'])
def webhook():
    update = request.get_json(force=True)
    bot.process_new_updates([telebot.types.Update.de_json(update)])
    return "OK", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)
