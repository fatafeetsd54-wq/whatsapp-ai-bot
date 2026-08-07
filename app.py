from flask import Flask, request
import requests
import os

app = Flask(__name__)

VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")
WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")


@app.route("/")
def home():
    return "WhatsApp AI Bot is running!"


@app.route("/health")
def health():
    return {"status": "ok"}


# Meta Webhook Verification
@app.route("/webhook", methods=["GET"])
def verify():
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        return challenge, 200

    return "Verification failed", 403


# Receive Messages
@app.route("/webhook", methods=["POST"])
def webhook():

    data = request.get_json()

    try:
        entry = data["entry"][0]
        changes = entry["changes"][0]
        value = changes["value"]

        if "messages" in value:

            message = value["messages"][0]
            from_number = message["from"]

            if "text" in message:
                user_text = message["text"]["body"]

                send_message(from_number, f"لقد استلمت رسالتك: {user_text}")

    except Exception as e:
        print(e)

    return "EVENT_RECEIVED", 200


def send_message(to, text):

    url = f"https://graph.facebook.com/v23.0/{PHONE_NUMBER_ID}/messages"

    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }

    body = {
        "messaging_product": "whatsapp",
        "to": to,
        "text": {
            "body": text
        }
    }

    requests.post(url, headers=headers, json=body)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
