import os
import time
import telebot
from openai import OpenAI

# Read secrets from environment (Koyeb will set these)
BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not BOT_TOKEN or not OPENAI_API_KEY:
    raise SystemExit("ERROR: BOT_TOKEN and OPENAI_API_KEY must be set as environment variables.")

# Init clients
bot = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML")
client = OpenAI(api_key=OPENAI_API_KEY)

@bot.message_handler(commands=["start", "help"])
def send_welcome(message):
    text = ("👋 Welcome to AI Doubt Solver!\n\n"
            "Send me a NEET/JEE doubt in text (Gujarati or English) and I'll explain in a simple way.")
    bot.reply_to(message, text)

@bot.message_handler(func=lambda m: True, content_types=['text'])
def handle_question(message):
    user_text = message.text.strip()
    chat_id = message.chat.id
    bot.send_chat_action(chat_id, "typing")
    prompt = f"Explain this NEET/JEE doubt in a simple Gujarati + English mix:\n\nQuestion: {user_text}\n\nAnswer:"

    try:
        # create chat completion (adjust model if you want)
        resp = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=800,
            temperature=0.3
        )
        answer = resp.choices[0].message.content.strip()
        # Send answer in chunks if long
        for chunk in [answer[i:i+4000] for i in range(0, len(answer), 4000)]:
            bot.send_message(chat_id, chunk)
    except Exception as e:
        bot.send_message(chat_id, "⚠️ Sorry, an error occurred. Try again later.")
        print("Error while getting completion:", e)

if __name__ == "__main__":
    print("Bot started. polling...")
    # Keep bot alive with retry on failures
    while True:
        try:
            bot.infinity_polling(timeout=60, long_polling_timeout=60)
        except Exception as e:
            print("Polling error:", e)
            time.sleep(5)
