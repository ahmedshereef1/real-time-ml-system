import json
import time

import requests
from loguru import logger

from trades.trade import Trade


class KrakenOHLCAPI:
    URL = 'https://api.kraken.com/0/public/OHLC'

    def __init__(self, product_id: str, last_n_days: int, interval_minutes: int = 1):
        self.product_id = product_id
        self.interval_minutes = interval_minutes
        self._is_done = False
        self._seen_candle_ts: set[int] = set()

        # Kraken OHLC 'since' is unix timestamp in seconds.
        self.since_timestamp_sec = int(time.time() - last_n_days * 24 * 60 * 60)
        self._last_cursor_sec = 0

    def _ohlc_to_synthetic_trades(self, candle: list) -> list[Trade]:
        # Kraken OHLC row format: [time, open, high, low, close, vwap, volume, count]
        ts_sec = int(candle[0])
        open_price = float(candle[1])
        high_price = float(candle[2])
        low_price = float(candle[3])
        close_price = float(candle[4])
        volume = float(candle[6])

        # Emit deterministic synthetic trades so candle aggregation reconstructs OHLC.
        q = volume / 4 if volume > 0 else 0.0
        prices = [open_price, high_price, low_price, close_price]

        return [
            Trade.from_kraken_rest_api_response(
                product_id=self.product_id,
                price=price,
                quantity=q,
                timestamp_sec=ts_sec + idx * 0.001,
            )
            for idx, price in enumerate(prices)
        ]

    def get_trades(self) -> list[Trade]:
        if self._is_done:
            return []

        headers = {'Accept': 'application/json'}
        params = {
            'pair': self.product_id,
            'interval': self.interval_minutes,
            'since': self.since_timestamp_sec,
        }

        try:
            response = requests.request('GET', self.URL, headers=headers, params=params)
        except requests.exceptions.RequestException as e:
            logger.error(f'Kraken OHLC API request failed for {self.product_id}: {e}')
            time.sleep(3)
            return []

        try:
            data = json.loads(response.text)
            candles = data['result'][self.product_id]
            new_cursor_sec = int(float(data['result']['last']))
        except (KeyError, ValueError, json.JSONDecodeError) as e:
            logger.error(f'Failed to parse OHLC response for {self.product_id}: {e}')
            return []

        all_trades: list[Trade] = []
        now_sec = int(time.time())

        for candle in candles:
            candle_ts = int(candle[0])
            if candle_ts in self._seen_candle_ts:
                continue

            # Skip the current in-progress minute candle from the exchange.
            if candle_ts >= now_sec - 60:
                continue

            self._seen_candle_ts.add(candle_ts)
            all_trades.extend(self._ohlc_to_synthetic_trades(candle))

        self.since_timestamp_sec = new_cursor_sec

        # Stop when cursor stops advancing or reaches near-now.
        if new_cursor_sec <= self._last_cursor_sec or new_cursor_sec >= now_sec - 60:
            self._is_done = True
        self._last_cursor_sec = new_cursor_sec

        return all_trades

    def is_done(self) -> bool:
        return self._is_done


class KrakenOHLCMultiAPI:
    def __init__(
        self, product_ids: list[str], last_n_days: int, interval_minutes: int = 1
    ):
        self._clients = [
            KrakenOHLCAPI(
                product_id=product_id,
                last_n_days=last_n_days,
                interval_minutes=interval_minutes,
            )
            for product_id in product_ids
        ]

    def get_trades(self) -> list[Trade]:
        all_trades: list[Trade] = []

        for client in self._clients:
            if client.is_done():
                continue
            all_trades.extend(client.get_trades())

        all_trades.sort(key=lambda trade: trade.timestamp_ms)
        return all_trades

    def is_done(self) -> bool:
        if not self._clients:
            return True
        return all(client.is_done() for client in self._clients)
