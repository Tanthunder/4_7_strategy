import yfinance as yf
from datetime import datetime, timedelta
import pandas as pd

ticker = 'RELIANCE.NS'

try:
    stock_data = yf.Ticker(ticker).info
    current_price = stock_data["regularMarketPrice"]
    print(current_price)

except :
    print("errorrrrrrrrrrrrrr...")
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=1)
    data = yf.download(ticker, start=start_date, end=end_date, interval="1h")
    time = "13:15:00" 
    data = data[data.index.time == pd.to_datetime(time).time()]
    datalist = data['Adj Close'].tolist()
    adj_close_data = [round(i,2) for i in datalist]
    current_price = adj_close_data[0]
    print(current_price)

