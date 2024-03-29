import os
import json
import pandas as pd
import datetime as dt
from oandapyV20 import API
from pprint import pprint
from typing import List, Dict, Tuple
import oandapyV20.endpoints.orders as orders
import oandapyV20.endpoints.trades as trades
import oandapyV20.endpoints.pricing as pricing
import oandapyV20.contrib.requests as requests
import oandapyV20.endpoints.accounts as accounts
import oandapyV20.endpoints.instruments as instruments
from credentials import OANDA_API_KEY, TEST_ACCOUNT_ID


class OandaData:

    def __init__(self, api_key, accountID) -> None:
        self.client = API(api_key)
        self.acctID = accountID

    def get_balance(self):
        resp = self.client.request(accounts.AccountSummary(self.acctID))
        return float(resp["account"]["balance"])

    def get_ohlc(self, symbol: str, count: int, interval: str):
        r = instruments.InstrumentsCandles(instrument=symbol,
                                           params={"count": count,
                                                    "granularity": interval,
                                                    "dailyAlignment": 17})
        resp = self.client.request(r)

        data = {"Date": [], "Open": [], "High": [], "Low": [], "Close": []}

        for candle in resp["candles"]:
            date = candle['time'].replace('T', ' ')[:candle['time'].index('.')]
            data["Date"].append(dt.datetime.strptime(date, "%Y-%m-%d %H:%M:%S"))
            data["Open"].append(float(candle["mid"]["o"]))
            data["High"].append(float(candle["mid"]["h"]))
            data["Low"].append(float(candle["mid"]["l"]))
            data["Close"].append(float(candle["mid"]["c"]))

        df = pd.DataFrame(data)
        df.set_index("Date", inplace=True)
        return df

    def get_current_low(self, symbol, count, interval):
        r = instruments.InstrumentsCandles(instrument=symbol,
                                           params={"count": count,
                                                    "granularity": interval,
                                                    "dailyAlignment": 17})
        resp = self.client.request(r)
        most_recent_low = float(resp['candles'][-1]['mid']['l'])
        return most_recent_low

    def get_current_high(self, symbol, count, interval):
        r = instruments.InstrumentsCandles(instrument=symbol,
                                           params={"count": count,
                                                    "granularity": interval,
                                                    "dailyAlignment": 17})
        resp = self.client.request(r)
        most_recent_high = float(resp['candles'][-1]['mid']['h'])
        return most_recent_high


    def get_current_ask_bid_price(self, symbol: str) -> Tuple[float]:
        r = pricing.PricingInfo(accountID=self.acctID,
                                params={"instruments": symbol})
        resp = self.client.request(r)
        ask_price = float(resp["prices"][0]["closeoutAsk"])
        bid_price = float(resp["prices"][0]["closeoutBid"])
        return (ask_price, bid_price)

    def calculate_MA(self, symbol: str, period: int, interval: str):
        df = self.get_ohlc(symbol, period + 3, interval)
        ma = df['Close'].rolling(period).mean().iloc[-1]
        return ma

    def calculate_ATR(self, symbol: str, period: int, interval: str):
        df = self.get_ohlc(symbol, period + 3, interval)
        # https://stackoverflow.com/questions/40256338/calculating-average-true-range-atr-on-ohlc-data-with-python
        # https://stackoverflow.com/questions/35753914/calculating-average-true-range-column-in-pandas-dataframe
        df["RangeOne"] = abs(df["High"] - df["Low"])
        df["RangeTwo"] = abs(df["High"] - df["Close"].shift())
        df["RangeThree"] = abs(df["Close"].shift() - df["Low"])
        df["TrueRange"] = df[["RangeOne", "RangeTwo", "RangeThree"]].max(axis=1)
        df["ATR"] = df["TrueRange"].ewm(span=period).mean()
        return df["ATR"].iloc[-1]

    def calculate_prev_min_low(self, symbol: str, period: int, interval: str):
        df = self.get_ohlc(symbol, period, interval)
        return min(df['Low'])

    def calculate_prev_max_high(self, symbol: str, period: int, interval: str):
        df = self.get_ohlc(symbol, period, interval)
        return max(df['High'])

if __name__ == "__main__":
    pass




