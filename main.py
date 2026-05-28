import time
from datetime import datetime
import pytz
from apscheduler.schedulers.background import BackgroundScheduler
from config import ALL_PAIRS, LOOP_INTERVAL_SECONDS, TIMEZONE, TP_PERCENT, SCORE_S_RANK, SCORE_A_PLUS, SCORE_A, LOOKBACK_CANDLES
from data_fetcher import OANDAClient, BinanceClient
from smc_detector import SMCDetector
from telegram_alert import send_telegram_message, format_alert
from logger import log_signal, generate_daily_summary
from news_filter import is_high_impact_news
from utils import rate_limit

oanda = OANDAClient()
binance = BinanceClient()

def analyze_pair(symbol):
    if symbol.endswith("_PERP"):
        df = binance.get_candles(symbol, LOOKBACK_CANDLES)
    else:
        df = oanda.get_candles(symbol, LOOKBACK_CANDLES)
    if df.empty:
        return None

    detector = SMCDetector(df)
    setups = detector.find_high_probability_setups()
    if not setups:
        return None

    best = max(setups, key=lambda x: x['score'])
    score = best['score']

    if score >= SCORE_S_RANK:
        rating = "S-Rank"
    elif score >= SCORE_A_PLUS:
        rating = "A+"
    elif score >= SCORE_A:
        rating = "A"
    else:
        return None

    tp1, tp2 = TP_PERCENT[rating]
    best['tp1_percent'] = tp1
    best['tp2_percent'] = tp2

    if is_high_impact_news(symbol):
        return None

    log_signal(symbol, best, rating)
    msg = format_alert(symbol, best, rating, tp1, tp2)
    send_telegram_message(msg)
    return best

def run_analysis():
    tz = pytz.timezone(TIMEZONE)
    print(f"[{datetime.now(tz)}] Scanning {len(ALL_PAIRS)} pairs...")
    for sym in ALL_PAIRS:
        analyze_pair(sym)
        rate_limit(1.5)
    print("Scan complete.")

def daily_summary_job():
    summary = generate_daily_summary()
    if summary:
        send_telegram_message(summary)

if __name__ == "__main__":
    print("Starting SMC Bot (flat version)...")
    scheduler = BackgroundScheduler(timezone=TIMEZONE)
    scheduler.add_job(run_analysis, 'interval', seconds=LOOP_INTERVAL_SECONDS)
    scheduler.add_job(daily_summary_job, 'cron', hour=0, minute=0)
    scheduler.start()
    try:
        while True:
            time.sleep(60)
    except KeyboardInterrupt:
        print("Stopped.")
        scheduler.shutdown()
