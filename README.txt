Sonic Koyeb AI Doubt Solver - README

Files:
- main.py
- requirements.txt
- Procfile

Deployment on Koyeb:
1. Push this folder to GitHub or zip and upload per Koyeb instructions.
2. Create a new App on Koyeb and connect the repo.
3. Set Environment Variables in Koyeb:
   - BOT_TOKEN = <your telegram bot token>
   - OPENAI_API_KEY = <your openai api key>
   - OWNER_ID (optional) = 7447651332
   - ALLOWED_GROUP_ID (optional) = -1002432150473
4. Build command: pip install -r requirements.txt
5. Start command: leave blank (Procfile will be used) or use: gunicorn main:app
6. After deployment, set webhook:
   https://api.telegram.org/bot<BOT_TOKEN>/setWebhook?url=https://<your-app-name>.koyeb.app/<BOT_TOKEN>

Notes:
- This version does not include OCR to keep dependencies lightweight. For image-to-text, add an OCR library or API.
- Authorized users are stored in memory (will reset if the app restarts). For persistence, integrate a small DB.
