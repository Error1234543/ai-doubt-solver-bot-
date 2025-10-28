==============================
🇮🇳 Gujarati AI Doubt Bot (Render)
==============================

🧠 Features:
- NEET/JEE Gujarati AI Doubt Solver
- Text + Image question support
- Only owner and authorized users allowed
- Works only inside one Telegram group

------------------------------
🚀 How to Deploy on Render
------------------------------

1️⃣ Go to https://render.com → Create New → Web Service

2️⃣ Connect your GitHub repo or upload this ZIP folder

3️⃣ In Render Settings:
   - Build Command:
       pip install -r requirements.txt
   - Start Command:
       gunicorn ai_doubt_bot_render:app --workers 1 --bind 0.0.0.0:$PORT

4️⃣ Add Environment Variables:
   BOT_TOKEN = your telegram bot token
   OPENAI_API_KEY = your openai key
   OWNER_ID = your telegram id (default 7447651332)
   GROUP_ID = your group id (-100xxxxx)
   WEBHOOK_URL = https://<your-render-domain>.onrender.com/webhook

5️⃣ Deploy and wait for build completion

6️⃣ Once deployed, open in browser:
   https://<your-render-domain>.onrender.com/set_webhook
   → This registers the bot with Telegram.

7️⃣ Done! Your bot is live!

------------------------------
🧾 Commands (Owner only)
------------------------------
/auth <telegram_id>       → authorize user
/auth remove <telegram_id>→ remove user
/auth list                → show authorized users

Only authorized users can use the bot inside your selected group.

------------------------------
👨‍💻 Support
------------------------------
Made for Gujarati NEET/JEE AI doubt solving.
