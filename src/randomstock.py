import random
import webbrowser
import pandas as pd
import time
import yfinance as yf

#A superclass for making filters or any other settings
class Setting:
	def __init__(self, name, status=True):
		self.name = name
		self.status = status
	def apply(self, ticker):
		return True
	def print(self):
		print(f"Filter Name: {self.name}, status={self.status}")

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
					print(f"{ticker} passed the price filter: {price:.2f} meets the threshold ({self.comparison} {self.price}).")
					return True
		except Exception:
			return False
		return False
	
	def print(self):
		print(f"Filter Name: {self.name}")
		print(f"VARIABLES: status={self.status}, price-value={self.price}, comparison-method=\"{self.comparison}\"")

	def adjust(self):
		switch = input("Enter nothing to turn on this filter, vice versa: ")
		self.status = True
		if (switch != ""):
			self.status = False
			return
		self.price = ""
		while (self.price.isdigit() == False):
			self.price = input("Please input an integer value for price-value: ")
		self.price = int(self.price)
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
                    print(f"{ticker} passed the market-cap filter: {market_cap:.2f}M meets the threshold ({self.comparison} {self.market_cap}M).")
                    return True
        except Exception:
            return False
        return False
    
    def print(self):
        print(f"Filter Name: {self.name}")
        print(f"VARIABLES: status={self.status}, market_cap-value={self.market_cap}M, comparison-method=\"{self.comparison}\"")
    
    def adjust(self):
        
        val = ""
        while not val.isdigit():
            val = input("Please input an integer value for market cap (in million USD): ")
        self.market_cap = int(val)
        comparison = ""
        while comparison not in (">=", "<="):
            comparison = input("Please input \"<=\" or \">=\" for comparison method: ")
        self.comparison = comp
        print(f"\nVARIABLES: status={self.status}, market_cap-value={self.market_cap}M, comparison-method=\"{self.comparison}\"\n")




def settings_panel(filters):
	while(True):
		print("===========================================\nSettings control panel\n===========================================")
		i = 1
		for filter in filters:
			print(f"{i}. ", end="")
			filter.print()
			i=i+1
		i = "" 
		print()
		while (i.isdigit() == False and i!="-1"):
			i = input("Which filter would you wish to configure? Enter -1 to exit: ")
		i = int(i)
		if (i > 0 and i-1 < len(filters)):
			filters[i-1].adjust()
		else:
			return 0


def apply_filters(tickers, filters):
	qualified = False
	count = -1
	while (qualified != True):
		count = count+1
		qualified = True
		ticker = random.choice(tickers)
		if (count > 25): 
			print()
			print("Filter application failed after 25 retries — the filters appear to be too strict for the current data. Consider relaxing the filter criteria or reviewing the input parameters.\n")
			return None
		elif count > 15: 
			print(f"Retry {count}: ")
		for filter in filters:
			info = yf.Ticker(ticker).info
			if (filter.apply(ticker, info) != True):
				qualified = False
				break
	return ticker
		
print("Fast TradingView access to a random stock, with basic filters.")
print("Downloading latest data...\n")
df = pd.read_csv("https://www.nasdaqtrader.com/dynamic/symdir/nasdaqlisted.txt", sep='|')
#The last row is a summary which is marked by file creation time
df = df[~df['Symbol'].str.contains('File Creation Time', na=False)]
nasdaq_tickers = df.dropna(subset=['Symbol'])  #Drop nan values
nasdaq_tickers = df['Symbol'].astype(str).str.strip()  #Convert all into strings
exchange="NASDAQ"
price_filter = PriceScreenSetting()
marketcap_filter = MarketCapScreenSetting()
filters = []
filters.append(price_filter)
filters.append(marketcap_filter)
str = ""
while (str == ""):
	print("Control: Enter nothing to continue, Enter \"settings\" to access filter settings.")
	str=input("Enter your option: ")
	if (str==""):
		print("Filtering stocks...")
		ticker = apply_filters(nasdaq_tickers, filters)
		if (ticker == None):
			continue
		url = f"https://www.tradingview.com/chart/?symbol={exchange}:{ticker}"
		webbrowser.open(url)
		time.sleep(0.3)
		print()
	if (str=="settings"):
		print()
		settings_panel(filters)
		str=""
		print()
print("Exiting Program...")
exit()