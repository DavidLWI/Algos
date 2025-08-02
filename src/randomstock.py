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

def apply_filters(tickers, filters):
	qualified = False
	while (qualified != True):
		qualified = True
		ticker = random.choice(tickers)
		for filter in filters:
			if (filter.apply(ticker) != True):
				qualified = False
				break
	return ticker
		
print("This program aims to provide fast tradingview access to a randomly selected stock, with customized basic filters.\n")
print("Control: Enter nothing to continue, Enter \"filters\" to access filter settings.\n")
df = pd.read_csv("https://www.nasdaqtrader.com/dynamic/symdir/nasdaqlisted.txt", sep='|')
#The last row is a summary which is marked by file creation time
df = df[~df['Symbol'].str.contains('File Creation Time', na=False)]
nasdaq_tickers = df.dropna(subset=['Symbol'])  #Drop nan values
nasdaq_tickers = df['Symbol'].astype(str).str.strip()  #Convert all into strings
exchange="NASDAQ"
price_filter = PriceScreenSetting()
filters = []
filters.append(price_filter)
str = ""
while (str == ""):
	ticker = apply_filters(nasdaq_tickers, filters)
	url = f"https://www.tradingview.com/chart/?symbol={exchange}:{ticker}"
	webbrowser.open(url)
	time.sleep(0.3)
	print()
	str=input("Do you wish to continue? (Enter nothing to continue)")
print("Exiting Program...")
exit()


