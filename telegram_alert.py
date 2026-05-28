import requests
from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID

def send_telegram_message(message):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("Telegram credentials missing")
        return False
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "HTML"}
    try:
        r = requests.post(url, json=payload, timeout=10)
        r.raise_for_status()
        return True
    except Exception as e:
        print(f"Telegram error: {e}")
        return False

def format_alert(symbol, setup, rating, tp1_pct, tp2_pct):
    direction = "🟢 BUY" if setup['type'] == 'bullish' else "🔴 SELL"
    if rating == "S-Rank":
        emoji = "🔥🔥🔥"
    elif rating == "A+":
        emoji = "⭐"
    else:
        emoji = "✅"
    msg = (
        f"{emoji} <b>SMC {rating}</b> {emoji}\n"
        f"📊 {symbol}\n"
        f"{direction}\n"
        f"📍 Entry ~ {setup['price_level']:.5f}\n"
        f"🎯 TP1 +{tp1_pct}%\n"
        f"🎯 TP2 +{tp2_pct}%\n"
        f"📈 Score: {setup['score']}/100\n"
        f"⏰ {setup['timestamp'].strftime('%H:%M %d-%b')}\n"
        f"#SMC #{symbol.replace('_','')}"
    )
    return msg
