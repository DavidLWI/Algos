import random
import webbrowser
import pandas as pd
import time

df = pd.read_csv("https://www.nasdaqtrader.com/dynamic/symdir/nasdaqlisted.txt", sep='|')
#The last row is a summary which is marked by file creation time
df = df[~df['Symbol'].str.contains('File Creation Time', na=False)]
nasdaq_tickers = df['Symbol'].tolist()
exchange="NASDAQ"
#Random pick a stock
str = ""
while (str == ""):
	ticker = random.choice(nasdaq_tickers)
	url = f"https://www.tradingview.com/chart/?symbol={exchange}:{ticker}"
	webbrowser.open(url)
	time.sleep(0.5)
	str=input("Do you wish to continue? (Enter nothing to continue)")
print("Exiting Program...")
exit()


