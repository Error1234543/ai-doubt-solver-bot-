import os
from flask import Flask, request
import telebot
import openai

# ---------- CONFIG (set these in Koyeb environment variables) ----------
BOT_TOKEN = os.getenv("BOT_TOKEN")          # e.g. 123456:ABCxyz
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OWNER_ID = int(os.getenv("OWNER_ID", "8226637107"))           # change if you want
ALLOWED_GROUP_ID = int(os.getenv("ALLOWED_GROUP_ID", "-1003126293720"))  # change to your group id
# ---------------------------------------------------------------------

if not BOT_TOKEN or not OPENAI_API_KEY:
    raise RuntimeError("Set BOT_TOKEN and OPENAI_API_KEY in environment variables.")

openai.api_key = OPENAI_API_KEY
bot = telebot.TeleBot(BOT_TOKEN, threaded=False)
app = Flask(__name__)

# Simple in-memory authorized set (persist only while app runs)
AUTHORIZED = {OWNER_ID}

# Owner command to add authorized user
@bot.message_handler(commands=['auth'])
def cmd_auth(message):
    if message.from_user.id != OWNER_ID:
        bot.reply_to(message, "Only owner can authorize users.")
        return
    parts = message.text.strip().split()
    if len(parts) == 2 and parts[1].isdigit():
        uid = int(parts[1])
        AUTHORIZED.add(uid)
        bot.reply_to(message, f"✅ Authorized {uid}")
    elif len(parts) == 2 and parts[1].lower() == "list":
        bot.reply_to(message, f"Authorized users: {sorted(list(AUTHORIZED))}")
    elif len(parts) == 3 and parts[1].lower()=="remove" and parts[2].isdigit():
        uid = int(parts[2])
        AUTHORIZED.discard(uid)
        bot.reply_to(message, f"Removed {uid}")
    else:
        bot.reply_to(message, "Usage: /auth <user_id>  |  /auth list  |  /auth remove <id>")

# Helper: call OpenAI ChatCompletion (simple)
def ask_openai(prompt):
    try:
        resp = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role":"system", "content":"You are a helpful tutor answering NEET/JEE science questions in Gujarati. Keep explanations clear and concise."},
                {"role":"user", "content": prompt}
            ],
            max_tokens=800,
            temperature=0.2
        )
        return resp.choices[0].message['content'].strip()
    except Exception as e:
        return f"Error contacting OpenAI: {e}"

# Handle text doubts
@bot.message_handler(content_types=['text'])
def handle_text(message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    # Only respond in allowed group or owner can use anywhere
    if user_id != OWNER_ID and chat_id != ALLOWED_GROUP_ID:
        # ignore or inform
        return
    if user_id != OWNER_ID and user_id not in AUTHORIZED:
        bot.reply_to(message, "🔒 You are not authorized. Contact the owner.")
        return

    bot.send_chat_action(chat_id, 'typing')
    prompt = f"વહ પ્રશ્ન છે: {message.text}\nજવાબ ગુજરાતી માં NEET/JEE સ્તર પ્રમાણે વિસ્તૃત પરંતુ concise આપો."
    answer = ask_openai(prompt)
    bot.reply_to(message, answer)

# Handle photos (we pass photo URL to the model; OCR isn't included to keep dependencies light)
@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    if user_id != OWNER_ID and chat_id != ALLOWED_GROUP_ID:
        return
    if user_id != OWNER_ID and user_id not in AUTHORIZED:
        bot.reply_to(message, "🔒 You are not authorized. Contact the owner.")
        return
    try:
        file_info = bot.get_file(message.photo[-1].file_id)
        file_url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_info.file_path}"
        bot.reply_to(message, "📷 Photo received — analyzing. Give me a moment...")
        prompt = f"આ ઇમેજની લિંક છે: {file_url}\nફોટામાં જો પ્રશ્ન છે તો તે પ્રશ્નને સમજાવીને ગુજરાતીમાં NEET/JEE સ્તર પ્રમાણે જવાબ આપો."
        answer = ask_openai(prompt)
        bot.reply_to(message, answer)
    except Exception as e:
        bot.reply_to(message, f"Error processing photo: {e}")

# Flask webhook endpoint for Telegram
@app.route('/' + BOT_TOKEN, methods=['POST'])
def webhook():
    update = request.get_json(force=True)
    bot.process_new_updates([telebot.types.Update.de_json(update)])
    return '', 200

@app.route('/')
def index():
    return "Sonic Koyeb AI Doubt Solver is running!"

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
