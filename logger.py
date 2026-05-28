import json
from datetime import datetime, timedelta
import pytz
from config import TIMEZONE

LOG_FILE = "signals.log"

def log_signal(symbol, setup, rating):
    tz = pytz.timezone(TIMEZONE)
    now = datetime.now(tz)
    entry = {
        "timestamp": now.isoformat(),
        "symbol": symbol,
        "type": setup['type'],
        "score": setup['score'],
        "rating": rating,
        "price_level": setup['price_level']
    }
    try:
        with open(LOG_FILE, "a") as f:
            f.write(json.dumps(entry) + "\n")
    except Exception as e:
        print(f"Log error: {e}")

def generate_daily_summary():
    tz = pytz.timezone(TIMEZONE)
    today = datetime.now(tz).date()
    start_of_day = datetime.combine(today, datetime.min.time()).replace(tzinfo=tz)
    signals = []
    try:
        with open(LOG_FILE, "r") as f:
            for line in f:
                entry = json.loads(line.strip())
                ts = datetime.fromisoformat(entry['timestamp'])
                if ts >= start_of_day:
                    signals.append(entry)
    except FileNotFoundError:
        return None
    if not signals:
        return "📭 No SMC signals today."
    summary = f"📊 DAILY SUMMARY ({today})\n"
    summary += f"Total signals: {len(signals)}\n"
    summary += "---\n"
    for s in signals[-10:]:
        summary += f"{s['symbol']} {s['type'].upper()} | {s['rating']} (score {s['score']})\n"
    return summary
