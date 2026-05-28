# SMC Signal Bot

Automated Smart Money Concepts scanner for Forex, Indices, Metals (OANDA) and Crypto USD perpetuals (Binance). Sends Telegram alerts for A, A+, and S-Rank setups.

## Setup

1. Copy `.env.example` to `.env` and fill your keys.
2. Install dependencies: `pip install -r requirements.txt`
3. Run locally: `python main.py`
4. Deploy on Render using the Dockerfile + render.yaml.

## Telegram alerts format
- Direction, entry level, TP1%, TP2%, score, timestamp.
- Daily summary at midnight (WAT).
