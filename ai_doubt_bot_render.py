# ai_doubt_bot_render.py
import os
import json
import io
from pathlib import Path
from flask import Flask, request, abort
import telebot
from PIL import Image
import easyocr
import openai

# ----------------------------
# Configuration (fill these in Render Environment Variables)
# ----------------------------
BOT_TOKEN = os.getenv("BOT_TOKEN") or "YOUR_BOT_TOKEN_HERE"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY") or "YOUR_OPENAI_API_KEY_HERE"
OWNER_ID = int(os.getenv("OWNER_ID", "7447651332"))
GROUP_ID = int(os.getenv("GROUP_ID", "-1002432150473"))
WEBHOOK_URL = os.getenv("WEBHOOK_URL") or "https://your-render-domain.onrender.com/webhook"

if not BOT_TOKEN or not OPENAI_API_KEY:
    raise RuntimeError("Set BOT_TOKEN and OPENAI_API_KEY environment variables.")

openai.api_key = OPENAI_API_KEY
bot = telebot.TeleBot(BOT_TOKEN, threaded=False)
reader = easyocr.Reader(['gu','en'])

AUTH_FILE = Path("auth.json")

def load_auth():
    if not AUTH_FILE.exists():
        return {"authorized": []}
    with open(AUTH_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_auth(data):
    with open(AUTH_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def is_authorized(user_id):
    if user_id == OWNER_ID:
        return True
    data = load_auth()
    return int(user_id) in [int(x) for x in data.get("authorized", [])]

def add_authorized(user_id):
    data = load_auth()
    if int(user_id) not in data["authorized"]:
        data["authorized"].append(int(user_id))
        save_auth(data)

def remove_authorized(user_id):
    data = load_auth()
    if int(user_id) in data["authorized"]:
        data["authorized"].remove(int(user_id))
        save_auth(data)

def get_ai_answer(question_text):
    prompt = f"આ પ્રશ્નનો જવાબ ગુજરાતી ભાષામાં આપો, NEET/JEE સ્તર મુજબ સમજાવો:\n\n{question_text}"
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"⚠️ Error: {e}"

def allowed_in_context(user_id, chat_id, chat_type):
    if int(user_id) == OWNER_ID:
        return True
    if chat_type in ["group", "supergroup"] and int(chat_id) == GROUP_ID and is_authorized(user_id):
        return True
    return False

@bot.message_handler(commands=['auth'])
def cmd_auth(message):
    if message.from_user.id != OWNER_ID:
        bot.reply_to(message, "માત્ર Owner જ આ કમાન્ડ ચલાવી શકે છે.")
        return
    args = message.text.split()
    if len(args) < 2:
        bot.reply_to(message, "Use: /auth <id> | /auth remove <id> | /auth list")
        return
    if args[1] == "list":
        data = load_auth()
        bot.reply_to(message, f"Authorized IDs: {data['authorized']}")
        return
    if args[1] == "remove" and len(args) == 3:
        remove_authorized(int(args[2]))
        bot.reply_to(message, f"Removed {args[2]}")
        return
    add_authorized(int(args[1]))
    bot.reply_to(message, f"Authorized {args[1]} successfully!")

@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    if not allowed_in_context(user_id, chat_id, message.chat.type):
        bot.reply_to(message, "❌ આ બોટ માત્ર નિર્ધારિત ગ્રુપમાં જ કામ કરે છે અથવા તમારે owner દ્વારા authorise થવું જરૂરી છે.")
        return

    try:
        file_info = bot.get_file(message.photo[-1].file_id)
        downloaded = bot.download_file(file_info.file_path)
        result = reader.readtext(downloaded, detail=0)
        text = " ".join(result)
        if not text.strip():
            bot.reply_to(message, "ફોટામાંથી પ્રશ્ન ઓળખી શકાય્યો નથી.")
            return
        bot.reply_to(message, f"📖 પ્રશ્ન ઓળખાયો:\n{text}\n💭 જવાબ તૈયાર થઈ રહ્યો છે...")
        answer = get_ai_answer(text)
        bot.send_message(chat_id, f"✅ જવાબ:\n{answer}")
    except Exception as e:
        bot.reply_to(message, f"Error: {e}")

@bot.message_handler(func=lambda m: True, content_types=['text'])
def handle_text(message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    if not allowed_in_context(user_id, chat_id, message.chat.type):
        bot.reply_to(message, "❌ આ બોટ માત્ર નિર્ધારિત ગ્રુપમાં જ કામ કરે છે અથવા તમારે owner દ્વારા authorise થવું જરૂરી છે.")
        return

    bot.send_chat_action(chat_id, 'typing')
    answer = get_ai_answer(message.text)
    bot.send_message(chat_id, f"✅ જવાબ:\n{answer}")

# Flask webhook
from flask import Flask, request
app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def webhook():
    json_str = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return '', 200

@app.route('/set_webhook')
def set_webhook():
    bot.set_webhook(WEBHOOK_URL)
    return f"Webhook set to {WEBHOOK_URL}"

@app.route('/')
def index():
    return "AI Doubt Bot running on Render.", 200

if __name__ == "__main__":
    if not os.path.exists("auth.json"):
        save_auth({"authorized": []})
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5000")))
