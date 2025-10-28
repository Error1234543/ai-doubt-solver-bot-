import telebot
from flask import Flask, request
import openai
import os

# =======================
# 🔒 Configuration
# =======================
BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_TELEGRAM_BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "YOUR_OPENAI_API_KEY")
OWNER_ID = 7447651332  # replace later if needed
ALLOWED_GROUP_ID = -1002432150473  # replace with your Telegram group ID

openai.api_key = OPENAI_API_KEY

bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

# =======================
# 🔐 Authentication system
# =======================
authorized_users = set()

@bot.message_handler(commands=['auth'])
def auth_user(message):
    if message.from_user.id == OWNER_ID:
        try:
            user_id = int(message.text.split()[1])
            authorized_users.add(user_id)
            bot.reply_to(message, f"✅ User {user_id} authorized!")
        except:
            bot.reply_to(message, "⚠️ Usage: /auth <user_id>")
    else:
        bot.reply_to(message, "🚫 Only owner can authorize users.")


# =======================
# 🧠 AI Doubt Solver
# =======================
@bot.message_handler(content_types=['text', 'photo'])
def handle_message(message):
    # Group restriction
    if message.chat.id != ALLOWED_GROUP_ID:
        bot.reply_to(message, "❌ This bot only works in the official NEET/JEE group.")
        return

    # Auth restriction
    if message.from_user.id != OWNER_ID and message.from_user.id not in authorized_users:
        bot.reply_to(message, "🔒 You are not authorized to use this bot.")
        return

    # Image doubt
    if message.content_type == 'photo':
        bot.reply_to(message, "📷 Got your image! Analyzing your doubt... (image support will be added soon)")
        return

    # Text doubt
    user_text = message.text
    bot.send_chat_action(message.chat.id, 'typing')

    prompt = f"""You are an AI tutor that answers NEET/JEE doubts in Gujarati language.
Question: {user_text}
Answer in Gujarati with clear explanation.
"""

    try:
        completion = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}]
        )
        answer = completion.choices[0].message['content']
        bot.reply_to(message, "🧠 " + answer)
    except Exception as e:
        bot.reply_to(message, f"❌ Error: {e}")


# =======================
# 🌐 Flask webhook setup
# =======================
@app.route('/' + BOT_TOKEN, methods=['POST'])
def webhook():
    update = telebot.types.Update.de_json(request.stream.read().decode('utf-8'))
    bot.process_new_updates([update])
    return 'OK', 200


@app.route('/')
def index():
    return '🤖 AI Doubt Solver Bot is running on Render!'


if __name__ == '__main__':
    # Webhook URL example:
    # https://your-app-name.onrender.com/<BOT_TOKEN>
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
