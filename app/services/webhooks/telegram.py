import logging
import hmac
from typing import Any, Dict, Optional
import httpx
from app.services.webhooks.base import WebhookHandler, WebhookMessage
logger = logging.getLogger(__name__)

class TelegramWebhook(WebhookHandler):
    platform = "telegram"

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.bot_token = config.get("BOT_TOKEN", "")
        self.webhook_secret = config.get("WEBHOOK_SECRET", "")
        self.api_base = f"https://api.telegram.org/bot{self.bot_token}"

    def verify_request(self, headers: Dict[str, str], body: bytes) -> bool:
        """Verify Telegram webhook via secret_token header."""
        if not self.webhook_secret:
            return True
        token = headers.get("X-Telegram-Bot-Api-Secret-Token", "")
        return hmac.compare_digest(token, self.webhook_secret)

    def parse_message(self, data: Dict[str, Any]) -> Optional[WebhookMessage]:
        """Parse Telegram update object."""
        message = data.get("message") or data.get("edited_message")
        if not message:
            return None

        text = message.get("text", "")
        if not text:
            return None

        chat = message.get("chat", {})
        sender = message.get("from", {})

        return WebhookMessage(
            platform=self.platform,
            text=text,
            sender_id=str(sender.get("id", "")),
            chat_id=str(chat.get("id", "")),
            raw=data,
            metadata={
                "username": sender.get("username", ""),
                "first_name": sender.get("first_name", ""),
                "chat_type": chat.get("type", "private"),
                "message_id": message.get("message_id"),
            }
        )

    async def send_reply(self, chat_id: str, text: str) -> bool:
        """Send message via Telegram Bot API."""
        if not self.bot_token:
            logger.error("Telegram BOT_TOKEN not configured")
            return False
        
        chunks = [text[i:i+4096] for i in range(0, len(text), 4096)]
        
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                for chunk in chunks:
                    resp = await client.post(
                        f"{self.api_base}/sendMessage",
                        json={
                            "chat_id": chat_id,
                            "text": chunk,
                            # حذفنا سطر parse_mode لتجنب أخطاء Entities
                        }
                    )
                    if resp.status_code != 200:
                        logger.error(f"Telegram failed: {resp.text}")
                        return False
            return True
        except Exception as e:
            logger.error(f"Telegram error: {e}")
            return False