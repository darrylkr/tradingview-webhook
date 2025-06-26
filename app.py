from flask import Flask, request, abort
import requests
import os

app = Flask(__name__)

# --- Configuration ---
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
SECRET_KEY = os.getenv("SECRET_KEY")

# --- Function to Send Telegram Message ---
def send_telegram_message(message: str):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message}
    requests.post(url, data=payload)

# --- Webhook Route ---
@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    if data.get("key") != SECRET_KEY:
        abort(403, description="Forbidden: Invalid secret key")

    message = data.get("message", "⚠️ Alert received from TradingView!")
    send_telegram_message(message)

    return "OK", 200

@app.route('/check-env')
def check_env():
    return {
        "TELEGRAM_TOKEN_SET": bool(TELEGRAM_TOKEN),
        "CHAT_ID_SET": bool(CHAT_ID),
        "SECRET_KEY_SET": bool(SECRET_KEY)
    }

# --- Local Dev Entry Point ---
if __name__ == "__main__":
    app.run(debug=True)
