import os
import re
import asyncio
from datetime import datetime
from telethon import TelegramClient, events
from telethon.sessions import StringSession

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
            if 100000 <= price <= 300000:
                return price
    return None

def build_message(erbil_price, kirkuk_price, prev_kirkuk):
    now = datetime.now()
    time_str = now.strftime("%I:%M %p")
    date_str = now.strftime("%Y/%m/%d")
    if prev_kirkuk is None:
        trend = "📊"
        trend_text = "أول تحديث"
    elif kirkuk_price > prev_kirkuk:
        trend = "📈"
        trend_text = f"ارتفع من {prev_kirkuk:,}"
    elif kirkuk_price < prev_kirkuk:
        trend = "📉"
        trend_text = f"انخفض من {prev_kirkuk:,}"
    else:
        trend = "➡️"
        trend_text = "بدون تغيير"
    return f"""💵 بيش الدولار اليوم

🕐 {time_str} | {date_str}

📍 أربيل:  {erbil_price:,} دينار
📍 كركوك:  {kirkuk_price:,} دينار

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

        if "هەولێر" not in text:
            return

        erbil_price = extract_price(text)
        if erbil_price is None:
            return

        kirkuk_price = erbil_price + 200

        message = build_message(erbil_price, kirkuk_price, last_price)
        try:
            await client.send_message(TARGET_CHANNEL, message)
            last_price = kirkuk_price
            print(f"✅ أربيل: {erbil_price:,} | كركوك: {kirkuk_price:,}")
        except Exception as e:
            print(f"❌ خطأ: {e}")

    await client.run_until_disconnected()

asyncio.run(main())
