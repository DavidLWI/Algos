#!usr/bin/env python3/
"""
Trading-View Random Stock Selector
Open a random NASDAQ stock in browser that satisfied user-defined price, market-cap, and SMA filters
"""

from __future__ import annotations

import logging
import random
import time
import webbrowser

import pandas as pd
import yfinance as yf

# ==============================================================================
# Constants
# ==============================================================================

NASDAQ_LIST_URL = (
    "https://www.nasdaqtrader.com/dynamic/symdir/nasdaqlisted.txt"
)
MAX_RETRIES = 35
EXCHANGE = "NASDAQ"

# ==============================================================================
# Logging
# ==============================================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%H:%M:%S",
)

# ==============================================================================
# Utilities
# ==============================================================================

def prompt_integer(msg : str, *, min : int | None = None, max : int | None = None) -> int:
    # Prompt until the user gives a valid integer, then return the value of the integer
    while True:
        try:
            value = int(input(msg))
            if (min is not None and value < min) or (max is not None and value>max):
                raise ValueError
            return value
        except ValueError:
            logging.error(f"Invalid Input. Minimum Value = {min}")



def prompt_activate(name : str) -> bool:
    while True:
        try:
            cmd = input(f"Do you want to activate {name}? (y/n) ").lower()
            if cmd not in ("y", "n"):
                raise ValueError
            if cmd == "y":
                return True
            if cmd == "n":
                return False
        except ValueError:
            logging.error("Invalid Input.")



# ==============================================================================
# Filters
# ==============================================================================


#A superclass for making filters or any other settings
class Setting:
    def __init__(self, name, status=True):
        self.name = name
        self.status = status

    def apply(self, ticker):
        return True
    
    def print(self):
        print(f"{self.name}, active={self.status}")

    def func_activate(self):
        self.status = prompt_activate(self.name)



class PriceScreenSetting(Setting):

    def __init__(self, name="Price Filter", status=True, price=15, comparison='>='):
        super().__init__(name, status)
        self.price = price
        self.comparison = comparison

    def apply(self, ticker, info):

        if self.status == False:
            return True
        try:
            price = info.get('currentPrice')
            if price is not None:
                if ((self.comparison=='>=' and price >= self.price) or (self.comparison=='<=' and price <= self.price)):
                    return True
        except Exception:
            return False
        return False
    
    def adjust(self):
        self.func_activate()
        if self.status == False:
            return
        print(f"CURRENT: p-value = {self.price}, comparison-method = \"{self.comparison}\". ")

        self.price = prompt_integer("Please input an integer value for price-value: ", min=0)
        self.comparison = ""
        while self.comparison not in (">=", "<="):
            self.comparison = input("Please input \"<=\" or \">=\" for comparison method: ")
        print(f"\nVARIABLES: status={self.status}, price-value={self.price}, comparison-method=\"{self.comparison}\"\n")



class MarketCapScreenSetting(Setting):
    def __init__(self, name="Market Cap Filter", status=True, market_cap=300, comparison='>='):
        super().__init__(name, status)
        self.market_cap = market_cap
        self.comparison = comparison

    def apply(self, ticker, info):
        if not self.status:
            return True
        try:
            market_cap = info.get('marketCap')/1_000_000
            if market_cap is not None:
                if (self.comparison == '>=' and market_cap >= self.market_cap) or \
                    (self.comparison == '<=' and market_cap <= self.market_cap):
                    return True
        except Exception:
            return False
        return False

    def adjust(self):
        self.func_activate()
        if self.status == False:
            return
        print(f"CURRENT: market-cap = {self.market_cap}, comparison-method = \"{self.comparison}\". ")

        self.market_cap = prompt_integer("Please input an integer value for market cap (in million USD): ", min=0)
        comparison = ""
        while comparison not in (">=", "<="):
            comparison = input("Please input \"<=\" or \">=\" for comparison method: ")
        self.comparison = comparison
        print(f"\nVARIABLES: status={self.status}, market_cap-value={self.market_cap}M, comparison-method=\"{self.comparison}\"\n")



class SMAComparisonSetting(Setting):
    def __init__(self, name="SMA Comparison Filter", status=True, period=200, comparison='>='):
        super().__init__(name, status)
        self.period = period		# SMA period (e.g., 200)
        self.comparison = comparison 
    def apply(self, ticker, info):
        if self.status == False:
            return True
        try:
            # Download historical close prices for the ticker
            data = yf.Ticker(ticker).history(period=f'{self.period}d') 
            close_prices = data['Close']
            # If not enough data to compute SMA
            if len(close_prices) < self.period:
                return False
            # Calculate SMA for the specified period
            sma = close_prices.rolling(window=self.period).mean().iloc[-1]
            current_price = close_prices.iloc[-1]
            if sma is None or pd.isna(sma):
                return False
            if ((self.comparison == '>=' and current_price >= sma) or
                (self.comparison == '<=' and current_price <= sma)):
                return True
        except Exception:
            return False
        return False

    def adjust(self):
        self.func_activate()
        if self.status == False:
            return
        print(f"CURRENT: period = {self.period}, comparison-method = \"{self.comparison}\". ")

        self.period = prompt_integer("Please input a positive integer value for SMA period: ", min=0, max=MAX_PERIOD)
        self.comparison = ""
        while self.comparison not in (">=", "<="):
            self.comparison = input("Please input \"<=\" or \">=\" for comparison method: ")

        print(f"\nVARIABLES: status={self.status}, SMA period={self.period}, comparison-method=\"{self.comparison}\"\n")

# ==============================================================================
# Core Functions
# ==============================================================================

def load_nasdaq_tickers() -> list[str]:
    logging.info("Loading NASDAQ tickers...\n")
    df = pd.read_csv(NASDAQ_LIST_URL, sep='|')
    #The last row is a summary which is marked by file creation time
    df = df[~df['Symbol'].str.contains('File Creation Time', na=False)]
    nasdaq_tickers = df.dropna(subset=['Symbol'])  #Drop nan values
    nasdaq_tickers = df['Symbol'].astype(str).str.strip()  #Convert all into strings
    return nasdaq_tickers



def settings_panel(filters : list[Setting]) -> None:
    while(True):
        for i, filter in enumerate(filters, start=1):
            print(f"{i}. ", end="")
            filter.print()
        i = "" 
        print()
        while (i.isdigit() == False and i!="-1"):
            i = input("Which filter would you wish to configure? Enter -1 to exit: ")
        i = int(i)
        if (i > 0 and i-1 < len(filters)):
            filters[i-1].adjust()
        else:
            return None



def apply_filters(tickers : list[str], filters : list[Setting]) -> str | None:
    # Return a random qualified ticker
    qualified = False
    count = -1

    while (qualified != True):
        count = count+1
        qualified = True
        ticker = random.choice(tickers)

        if (count >= 15 and count%5 == 0):
            logging.info(f"Still Searching... ({count} retries)")

        if (count > MAX_RETRIES): 
            logging.info(f"Failed to find qualified ticker after {MAX_RETRIES} retries.\n")
            return None
        
        for filter in filters:
            info = yf.Ticker(ticker).info
            if (filter.apply(ticker, info) != True):
                qualified = False
                break

    logging.info(f"Found qualified ticker {ticker} after {count} retries.")
    return ticker



# ==============================================================================
# Main Program
# ==============================================================================

def main() -> None:
    tickers_list = load_nasdaq_tickers()

    filters = []
    filters.append(PriceScreenSetting())
    filters.append(MarketCapScreenSetting())
    filters.append(SMAComparisonSetting())

    cmd = ""
    while (True):
        cmd = input("Press Enter to run, type \"settings\" to configure, or \"q\" to quit: ").strip().lower()

        if (cmd==""):
            ticker = apply_filters(tickers_list, filters)
            if (ticker == None):
                continue

            url = f"https://www.tradingview.com/chart/?symbol={EXCHANGE}:{ticker}"
            webbrowser.open(url)
            time.sleep(0.5)
            print()

        if (cmd == "settings"):
            print()
            settings_panel(filters)
            cmd=""

        if (cmd == 'q'):
            logging.info("Exiting Program...")
            exit()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nInterrupted - exiting.")