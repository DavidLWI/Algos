import random
import webbrowser
import pandas as pd
import time
import yfinance as yf

class Setting:
	def __init__(self, name, status=True):
		self.name = name
		self.status = status
	def apply(self, ticker):
		return True

class PriceScreenSetting(Setting):
	def __init__(self, name="Price Filter", status=True, min_price=15):
		super().__init__(name, status)
		self.min_price = min_price
	def apply(self, ticker):
		if self.status == False:
			return True
		try:
			info = yf.Ticker(ticker).info
			price = info.get('regularMarketPrice')
			if (price >= self.min_price):
				print(f"A price screening filter is being applied with a minimum price {self.min_price}.")
				return True
		except Exception:
			return False
		return False


df = pd.read_csv("https://www.nasdaqtrader.com/dynamic/symdir/nasdaqlisted.txt", sep='|')
#The last row is a summary which is marked by file creation time
df = df[~df['Symbol'].str.contains('File Creation Time', na=False)]
nasdaq_tickers = df.dropna(subset=['Symbol'])  #Drop nan values
nasdaq_tickers = df['Symbol'].astype(str).str.strip()  #Convert all into strings
exchange="NASDAQ"
price_filter = PriceScreenSetting(min_price=15)
#Random pick a stock
str = ""
while (str == ""):
	ticker = random.choice(nasdaq_tickers)
	while (price_filter.apply(ticker) == False):
		ticker = random.choice(nasdaq_tickers)
	url = f"https://www.tradingview.com/chart/?symbol={exchange}:{ticker}"
	webbrowser.open(url)
	time.sleep(0.3)
	print()
	str=input("Do you wish to continue? (Enter nothing to continue)")
print("Exiting Program...")
exit()


