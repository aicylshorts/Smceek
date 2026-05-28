import pandas as pd
import numpy as np
from config import SWING_LOOKBACK, ATR_PERIOD, MIN_FVG_SIZE_ATR_MULTIPLE, LIQUIDITY_LOOKBACK

class SMCDetector:
    def __init__(self, df):
        self.df = df.copy()
        self.df.reset_index(inplace=True)
        self.n = len(self.df)
        self.atr = self._calculate_atr()
        self.swing_highs = []
        self.swing_lows = []
        self._find_swing_points()

    def _calculate_atr(self):
        high_low = self.df['high'] - self.df['low']
        high_close = (self.df['high'] - self.df['close'].shift()).abs()
        low_close = (self.df['low'] - self.df['close'].shift()).abs()
        tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        return tr.rolling(window=ATR_PERIOD).mean()

    def _find_swing_points(self):
        for i in range(SWING_LOOKBACK, self.n - SWING_LOOKBACK):
            if all(self.df.loc[i, 'high'] > self.df.loc[i-k, 'high'] for k in range(1, SWING_LOOKBACK+1)) and \
               all(self.df.loc[i, 'high'] > self.df.loc[i+k, 'high'] for k in range(1, SWING_LOOKBACK+1)):
                self.swing_highs.append(i)
            if all(self.df.loc[i, 'low'] < self.df.loc[i-k, 'low'] for k in range(1, SWING_LOOKBACK+1)) and \
               all(self.df.loc[i, 'low'] < self.df.loc[i+k, 'low'] for k in range(1, SWING_LOOKBACK+1)):
                self.swing_lows.append(i)

    def detect_fvg(self):
        fvgs = []
        for i in range(2, self.n - 1):
            if self.df.loc[i-1, 'low'] > self.df.loc[i+1, 'high']:
                size = self.df.loc[i-1, 'low'] - self.df.loc[i+1, 'high']
                if size > self.atr.iloc[i] * MIN_FVG_SIZE_ATR_MULTIPLE:
                    fvgs.append({'type': 'bullish', 'index': i, 'top': self.df.loc[i-1, 'low'], 'bottom': self.df.loc[i+1, 'high'], 'size': size})
            elif self.df.loc[i-1, 'high'] < self.df.loc[i+1, 'low']:
                size = self.df.loc[i+1, 'low'] - self.df.loc[i-1, 'high']
                if size > self.atr.iloc[i] * MIN_FVG_SIZE_ATR_MULTIPLE:
                    fvgs.append({'type': 'bearish', 'index': i, 'top': self.df.loc[i+1, 'low'], 'bottom': self.df.loc[i-1, 'high'], 'size': size})
        return fvgs

    def detect_order_blocks(self):
        obs = []
        for idx in self.swing_highs + self.swing_lows:
            if idx + 3 >= self.n:
                continue
            if self.df.loc[idx+1, 'close'] > self.df.loc[idx, 'high']:
                ob_idx = idx
                while ob_idx > 0 and self.df.loc[ob_idx, 'close'] < self.df.loc[ob_idx, 'open']:
                    ob_idx -= 1
                if ob_idx < idx:
                    obs.append({'type': 'bullish', 'index': ob_idx, 'top': self.df.loc[ob_idx, 'high'], 'bottom': self.df.loc[ob_idx, 'low']})
            elif self.df.loc[idx+1, 'close'] < self.df.loc[idx, 'low']:
                ob_idx = idx
                while ob_idx > 0 and self.df.loc[ob_idx, 'close'] > self.df.loc[ob_idx, 'open']:
                    ob_idx -= 1
                if ob_idx < idx:
                    obs.append({'type': 'bearish', 'index': ob_idx, 'top': self.df.loc[ob_idx, 'high'], 'bottom': self.df.loc[ob_idx, 'low']})
        return obs

    def detect_liquidity_sweep(self):
        sweeps = []
        for i in range(LIQUIDITY_LOOKBACK, self.n - 1):
            recent_highs = [self.df.loc[j, 'high'] for j in range(max(0,i-20), i) if j in self.swing_highs]
            recent_lows = [self.df.loc[j, 'low'] for j in range(max(0,i-20), i) if j in self.swing_lows]
            if recent_highs:
                if self.df.loc[i, 'high'] > max(recent_highs) and self.df.loc[i+1, 'close'] < self.df.loc[i, 'low']:
                    sweeps.append({'type': 'bearish', 'index': i, 'sweep_level': max(recent_highs), 'choch': True})
            if recent_lows:
                if self.df.loc[i, 'low'] < min(recent_lows) and self.df.loc[i+1, 'close'] > self.df.loc[i, 'high']:
                    sweeps.append({'type': 'bullish', 'index': i, 'sweep_level': min(recent_lows), 'choch': True})
        return sweeps

    def find_high_probability_setups(self):
        fvgs = self.detect_fvg()
        sweeps = self.detect_liquidity_sweep()
        setups = []
        for sweep in sweeps:
            fvg_count = sum(1 for f in fvgs if f['type'] == sweep['type'] and f['index'] > sweep['index'])
            score = 0
            if fvg_count > 0:
                score += 40
            if len(self.detect_order_blocks()) > 0:
                score += 35
            score += 25
            score = min(score, 100)
            setups.append({
                'type': sweep['type'],
                'timestamp': self.df.loc[sweep['index'], 'timestamp'],
                'price_level': sweep['sweep_level'],
                'score': score,
                'fvg_count': fvg_count
            })
        return setups
