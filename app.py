from flask import Flask, request, abort
import requests
import os
import threading
import time
import requests
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
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

@app.route("/heartbeat", methods=["GET"])
def heartbeat():
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    logging.info(f"💓 Heartbeat checked at {timestamp}")
    return {"status": "alive", "timestamp": time.time()}, 200



@app.route('/check-env')
def check_env():
    return {
        "TELEGRAM_TOKEN_SET": bool(TELEGRAM_TOKEN),
        "CHAT_ID_SET": bool(CHAT_ID),
        "SECRET_KEY_SET": bool(SECRET_KEY)
    }


def keep_alive():
    def ping():
        while True:
            try:
                res = requests.get("https://tradingview-webhook-rn3z.onrender.com/heartbeat")
                if res.status_code == 200:
                    logging.info("✅ Self-ping successful")
                else:
                    logging.warning(f"⚠️ Unexpected response code: {res.status_code}")
            except Exception as e:
                logging.error(f"❌ Self-ping failed: {e}")
            time.sleep(840)
    thread = threading.Thread(target=ping)
    thread.daemon = True
    thread.start()


# --- Local Dev Entry Point ---
if __name__ == "__main__":
    keep_alive()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
