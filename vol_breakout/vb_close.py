import os
import time
import datetime as dt
from demo_credentials import OANDA_API_KEY, TEST_ACCOUNT_ID, VOLATILITY_BREAKOUT
from oandaTrader import OandaTrader
# from fbprophet import Prophet

# Login
if os.name == 'nt':
    oanda = OandaTrader(OANDA_API_KEY, VOLATILITY_BREAKOUT)
if os.name == 'posix':
    oanda = OandaTrader(OANDA_API_KEY, VOLATILITY_BREAKOUT)

def close_trades():
    oanda.cancel_all_orders()
    oanda.close_all_trades()

if __name__ == '__main__':
    close_trades()
    print("Close Trades::: " + time.ctime())