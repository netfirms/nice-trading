import os
import asyncio
import httpx
from utils.logger import setup_logger

logger = setup_logger("telegram", "logs/telegram.log")

class TelegramBot:
    def __init__(self):
        self.token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.chat_id = os.getenv("TELEGRAM_CHAT_ID")
        self.base_url = f"https://api.telegram.org/bot{self.token}"

    async def send_message(self, text: str):
        if not self.token or not self.chat_id:
            logger.warning("Telegram token or Chat ID not configured. Skipping notification.")
            return

        payload = {
            "chat_id": self.chat_id,
            "text": text,
            "parse_mode": "HTML"
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(f"{self.base_url}/sendMessage", json=payload)
                if response.status_code != 200:
                    logger.error(f"Failed to send Telegram message: {response.text}")
        except Exception as e:
            logger.error(f"Error sending Telegram message: {e}")

    def notify_trade(self, symbol, side, amount, price):
        emoji = "📈" if side == "buy" else "📉"
        msg = f"{emoji} <b>Trade Executed</b>\n\n" \
              f"Symbol: <code>{symbol}</code>\n" \
              f"Side: <b>{side.upper()}</b>\n" \
              f"Amount: <code>{amount}</code>\n" \
              f"Price: <code>{price}</code>"
        
        # Run async in background if possible, or just log
        asyncio.create_task(self.send_message(msg))
