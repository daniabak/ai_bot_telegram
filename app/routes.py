import logging
from quart import Blueprint, request, jsonify
from app.services.webhooks.telegram import TelegramWebhook
from app.services.llm_api import generate_text
logger = logging.getLogger(__name__)
main = Blueprint("main", __name__)

# Load your config (simplified — use your own config loader)
import json
with open("app/config.json") as f:
    config = json.load(f)

telegram_config = config["WEBHOOKS"]["TELEGRAM"]
@main.route("/api/webhook/telegram", methods=["POST"])
async def webhook_telegram():
    """Telegram Bot webhook endpoint."""
    handler = TelegramWebhook(telegram_config)
    raw_body = await request.get_data()
    data = await request.get_json()
    headers = {k: v for k, v in request.headers}

    # 1. Verify the request is from Telegram
    if not handler.verify_request(headers, raw_body):
        return jsonify({"error": "Invalid signature"}), 403

    # 2. Parse the message
    message = handler.parse_message(data)
    if not message:
        return jsonify({"status": "ok"}), 200

    logger.info(f"Telegram message from {message.sender_id}: {message.text[:80]}")

    # 3. Generate AI response
    try:
        ai_response = generate_text(user_message=message.text)
    except Exception as e:
        logger.error(f"LLM error: {e}")
        ai_response = "Sorry, something went wrong. Please try again later."

    # 4. Send the reply
    sent = await handler.send_reply(message.chat_id, ai_response)
    if not sent:
        logger.warning(f"Failed to send reply to chat {message.chat_id}")

    return jsonify({"status": "ok"}), 200