import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt

df = yf.download("AAPL", start="2011-01-01", end="2021-12-31", progress=False)
print(f"Downloaded {len(df)} rows of data.")
print(df)





