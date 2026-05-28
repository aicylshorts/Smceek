import pandas as pd
import requests
import oandapyV20
import oandapyV20.endpoints.instruments as instruments
from config import OANDA_API_KEY, OANDA_ACCOUNT_ID, OANDA_HOSTNAME, TIMEFRAME, BINANCE_FUTURES_BASE_URL

class OANDAClient:
    def __init__(self):
        self.client = oandapyV20.API(access_token=OANDA_API_KEY, environment=OANDA_HOSTNAME.split('.')[0])
        self.account_id = OANDA_ACCOUNT_ID

    def get_candles(self, instrument, count=200):
        params = {"granularity": TIMEFRAME.upper(), "count": count, "price": "M"}
        request = instruments.InstrumentsCandles(instrument=instrument, params=params)
        try:
            response = self.client.request(request)
            candles = []
            for candle in response.get('candles', []):
                if candle['complete']:
                    candles.append({
                        'timestamp': pd.to_datetime(candle['time']),
                        'open': float(candle['mid']['o']),
                        'high': float(candle['mid']['h']),
                        'low': float(candle['mid']['l']),
                        'close': float(candle['mid']['c']),
                        'volume': candle.get('volume', 0)
                    })
            df = pd.DataFrame(candles)
            if not df.empty:
                df.set_index('timestamp', inplace=True)
            return df
        except Exception as e:
            print(f"OANDA error for {instrument}: {e}")
            return pd.DataFrame()

class BinanceClient:
    def __init__(self):
        self.base_url = BINANCE_FUTURES_BASE_URL

    def get_candles(self, symbol, count=200):
        endpoint = f"{self.base_url}/fapi/v1/klines"
        params = {"symbol": symbol, "interval": TIMEFRAME, "limit": count}
        try:
            resp = requests.get(endpoint, params=params, timeout=10)
            resp.raise_for_status()
            data = resp.json()
            candles = []
            for c in data:
                candles.append({
                    'timestamp': pd.to_datetime(c[0], unit='ms'),
                    'open': float(c[1]),
                    'high': float(c[2]),
                    'low': float(c[3]),
                    'close': float(c[4]),
                    'volume': float(c[5])
                })
            df = pd.DataFrame(candles)
            if not df.empty:
                df.set_index('timestamp', inplace=True)
            return df
        except Exception as e:
            print(f"Binance error for {symbol}: {e}")
            return pd.DataFrame()
