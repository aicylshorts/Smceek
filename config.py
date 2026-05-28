import os
from dotenv import load_dotenv

load_dotenv()

# ========== INSTRUMENTS ==========
FOREX_PAIRS = [
    "EUR_USD", "GBP_USD", "USD_JPY", "AUD_USD", "USD_CAD", "USD_CHF", "NZD_USD"
]
INDICES = [
    "US30_USD", "US100_USD", "NAS100_USD", "SPX500_USD", "GER30_EUR"
]
METALS = [
    "XAU_USD", "XAG_USD"
]
CRYPTO_PAIRS = [
    "BTCUSD_PERP", "ETHUSD_PERP", "SOLUSD_PERP"
]
ALL_PAIRS = FOREX_PAIRS + INDICES + METALS + CRYPTO_PAIRS

# ========== API CONFIGURATION ==========
OANDA_API_KEY = os.getenv("OANDA_API_KEY")
OANDA_ACCOUNT_ID = os.getenv("OANDA_ACCOUNT_ID")
OANDA_ACCOUNT_TYPE = os.getenv("OANDA_ACCOUNT_TYPE", "practice")
OANDA_HOSTNAME = "api-fxpractice.oanda.com" if OANDA_ACCOUNT_TYPE == "practice" else "api-fxtrade.oanda.com"

BINANCE_FUTURES_BASE_URL = "https://fapi.binance.com"

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# ========== TRADING PARAMETERS ==========
TIMEFRAME = "15m"
LOOKBACK_CANDLES = 200
ATR_PERIOD = 14
SWING_LOOKBACK = 5
MIN_FVG_SIZE_ATR_MULTIPLE = 0.3
LIQUIDITY_LOOKBACK = 20

SCORE_S_RANK = 90
SCORE_A_PLUS = 80
SCORE_A = 70

TP_PERCENT = {
    "S-Rank": (1.5, 3.0),
    "A+": (1.0, 2.0),
    "A": (0.75, 1.5)
}

LOOP_INTERVAL_SECONDS = 300
NEWS_BLACKOUT_MINUTES = 30
TIMEZONE = "Africa/Lagos"
