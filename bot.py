import os
import re
import asyncio
from datetime import datetime
from telethon import TelegramClient, events
from telethon.sessions import StringSession

BOT_TOKEN = os.environ.get("BOT_TOKEN")
API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
SESSION_STRING = os.environ.get("SESSION_STRING")

SOURCE_CHANNEL = "nrxidolar"
TARGET_CHANNEL = "besdolar"

last_price = None

def extract_price(text):
    if not text:
        return None
    patterns = [
        r'(\d{1,3}(?:,\d{3})+)',
        r'(\d{4,6})',
    ]
    for pattern in patterns:
        matches = re.findall(pattern, text)
        for match in matches:
            price = int(match.replace(',', ''))
            if 1000 <= price <= 2000:
                return price
    return None

def build_message(price, prev_price):
    now = datetime.now()
    time_str = now.strftime("%I:%M %p")
    date_str = now.strftime("%Y/%m/%d")
    if prev_price is None:
        trend = "📊"
        trend_text = "أول تحديث"
    elif price > prev_price:
        trend = "📈"
        trend_text = f"ارتفع من {prev_price:,}"
    elif price < prev_price:
        trend = "📉"
        trend_text = f"انخفض من {prev_price:,}"
    else:
        trend = "➡️"
        trend_text = "بدون تغيير"
    return f"""💵 بيش الدولار اليوم

🕐 {time_str} | {date_str}
💰 {price:,} دينار

{trend} {trend_text}

@besdolar"""

async def main():
    global last_price
    client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)
    await client.start()
    print("✅ البوت يعمل...")

    @client.on(events.NewMessage(chats=SOURCE_CHANNEL))
    async def handler(event):
        global last_price
        text = event.message.text or ""
        price = extract_price(text)
        if price is None:
            return
        message = build_message(price, last_price)
        try:
            await client.send_message(TARGET_CHANNEL, message)
            last_price = price
            print(f"✅ نُشر: {price:,}")
        except Exception as e:
            print(f"❌ خطأ: {e}")

    await client.run_until_disconnected()

asyncio.run(main())
