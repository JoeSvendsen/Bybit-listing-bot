# Detailed Installation & Launch Guide — Bybit Listing Notifier Bot

This guide explains, step-by-step, how to set up, configure, launch, test, export data from, and deploy the Bybit listing monitoring Telegram bot.

---
## 1. Prerequisites

- Python 3.10+ installed (`python3 --version`)
- (Optional but recommended) `git` for cloning
- Telegram account; create a bot via [BotFather](https://core.telegram.org/bots#botfather) and note the token
- The chat ID to receive alerts (see below)

---
## 2. Download the Bot Code
- If using git:
  ```sh
  git clone <YOUR_REPOSITORY_URL>
  cd <repository-folder>
  ```
- Or, download and unzip all project files to your desired location.

---
## 3. Install Python Dependencies
- Recommended: Use a virtual environment
  ```sh
  python3 -m venv venv && source venv/bin/activate
  pip install -r requirements.txt
  ```

---
## 4. Configure the Bot (.env Settings)
- Copy `.env` to your working directory (edit directly if it exists):
  - `TELEGRAM_BOT_TOKEN=<your-bot-token from BotFather>`
  - `TELEGRAM_CHAT_ID=<your-channel-or-group-or-user-chat-id>`
    - For private IDs: Message your bot, then visit `https://api.telegram.org/bot<your-bot-token>/getUpdates` to find your chat ID.
  - (Optional) Adjust:
    - `BOT_LOGLEVEL=INFO` or `DEBUG`
    - `BOT_LOGFILE=bot.log` (if you want file logs)

---
## 5. Launch the Bot
- Run:
  ```sh
  python main.py
  ```
- You should see startup logs. The bot will now poll Bybit’s API and send messages to your specified chat when it detects new listings.

---
## 6. Running the Test Suite
- To verify functionality:
  ```sh
  pip install pytest
  pytest test_main.py
  ```

---
## 7. Export Listing Database (CSV/JSON)
- Export known symbols to CSV:
  ```sh
  python export_db.py
  ```
- Export to JSON:
  ```sh
  python export_db.py json
  ```

---
## 8. (Optional) Docker/Cloud Deployment
- Build Docker image:
  ```sh
  docker build -t bybit-notify-bot .
  ```
- Launch (with database volume and .env):
  ```sh
  docker run --env-file .env -v $(pwd)/symbols.db:/app/symbols.db bybit-notify-bot
  ```
- For cloud deployment, see `deploy_cloud.sh` and edit for your provider (Heroku, AWS ECS, GCP Cloud Run, etc.)

---
## 9. Troubleshooting Tips
- Ensure you’re running Python 3.10 or higher
- Check logfile or console for errors
- Double-check that token and chat ID are correct and that your bot is allowed to send messages to the target chat
- For permission errors on chat: add bot to group/channel and make it an admin (if required)
- Restart the bot after any .env or dependency change

---
## 10. References and Support
- See `README.md` and `bybit-listing-guide.md` for additional architecture and config details.
- Core API docs:
  - Bybit: https://bybit-exchange.github.io/docs/v5/market/instrument
  - Telegram: https://core.telegram.org/bots/api

If you need command examples, custom scripts, or deployment help, ask your project maintainer or support contact!
