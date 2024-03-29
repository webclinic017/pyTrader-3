import os
import time
import datetime as dt
import numpy as np
from demo_credentials import OANDA_API_KEY, TEST_ACCOUNT_ID, VOLATILITY_BREAKOUT
from oandaTrader import OandaTrader
# from fbprophet import Prophet

# Login
if os.name == 'nt':
    oanda = OandaTrader(OANDA_API_KEY, VOLATILITY_BREAKOUT)
if os.name == 'posix':
    oanda = OandaTrader(OANDA_API_KEY, VOLATILITY_BREAKOUT)

INSTRUMENTS = oanda.fx_instruments()

RISK_PER_TRADE = 0.0002

ENTRY_BUFFER = 6

ORDERS_LIST = oanda.get_order_list()
TRADES_LIST = oanda.get_trade_list()

SYMBOLS_ORDERS = oanda.symbols_in_orders()
SYMBOLS_TRADES = oanda.symbols_in_trades()

DECIMAL_TABLE = oanda.create_decimal_table()

# def predict(symbol):
#     df = oanda.get_ohlc(symbol,24,'H1')
#     df = df.reset_index()
#     df['ds'] = df['Date']
#     df['y'] = df['Close']
#     data = df[['ds','y']]

#     end_date = get_start_time(symbol) + datetime.timedelta(days=1)

#     model = Prophet()
#     model.fit(data)

#     future = model.make_future_dataframe(periods=30, freq='h')
#     forecast = model.predict(future)
#     predicted_price = forecast[forecast['ds'] == end_date]['yhat']
#     return predicted_price

def conviction(symbol):
    df = oanda.get_ohlc(symbol, 6, 'D')
    df['conviction'] = abs((df['Close'] - df['Open']) / (df['High'] - df['Low']))

    df['strength'] = (df['Close'] - df['Open'])
    bullish = df[df['strength'] > 0]
    bearish = df[df['strength'] < 0]

    df = df[:-1]

    convince = df['conviction'].median() > 0.5
    bull = abs(bullish['strength'].sum()) > abs(bearish['strength'].sum())

    print(df)
    print(df['conviction'].median())

    return convince, bull

    # df['vol'] = np.where((df['Close'] - df['Open']) < 0, -1, 1)




def open_trades():
    #count = 0

    for symbol in INSTRUMENTS:
        #count += 1
        #print(f"{symbol}\t : \t {count}/{len(INSTRUMENTS)}")
        try:
            df = oanda.get_ohlc(symbol, 5, 'D')
            # print(symbol)
            # print(df)

            prev_high = df.iloc[-2]['High']
            prev_low = df.iloc[-2]['Low']

            atr = oanda.calculate_ATR(symbol, 10, 'D')

            convince, bullish = conviction(symbol)

            if symbol not in SYMBOLS_ORDERS and symbol not in SYMBOLS_TRADES:
                if bullish:
                    # bullish -> long at low
                    curr_ask = oanda.get_current_ask_bid_price(symbol)[0]

                    limit_long_entry = prev_low + (ENTRY_BUFFER / DECIMAL_TABLE[symbol]['multiple'])
                    limit_sl = limit_long_entry - atr
                    if curr_ask > limit_long_entry:
                        oanda.create_limit_order(symbol, limit_long_entry, limit_sl, RISK_PER_TRADE)

                    stop_long_entry = prev_high+(ENTRY_BUFFER / DECIMAL_TABLE[symbol]['multiple'])
                    stop_sl = stop_long_entry - atr
                    if curr_ask < stop_long_entry:
                        oanda.create_stop_order(symbol, stop_long_entry, stop_sl, RISK_PER_TRADE)
                else:
                    # bearish -> short at high
                    curr_bid = oanda.get_current_ask_bid_price(symbol)[1]

                    limit_short_entry = prev_high - (ENTRY_BUFFER / DECIMAL_TABLE[symbol]['multiple'])
                    limit_sl = limit_short_entry + atr
                    if curr_bid < limit_short_entry:
                        oanda.create_limit_order(symbol, limit_short_entry, limit_sl, RISK_PER_TRADE)

                    stop_short_entry = prev_low-(ENTRY_BUFFER / DECIMAL_TABLE[symbol]['multiple'])
                    stop_sl = stop_short_entry + atr
                    if curr_bid > stop_short_entry:
                        oanda.create_stop_order(symbol, stop_short_entry, stop_sl, RISK_PER_TRADE)

            time.sleep(1)
        except Exception as e:
            print(e)
            time.sleep(1)

if __name__ == '__main__':
    #open_trades()
    for symbol in INSTRUMENTS:
        print(symbol)
        print(conviction(symbol))
    print("Open Trades::: " + time.ctime())