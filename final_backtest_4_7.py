import yfinance as yf
from datetime import datetime, timedelta
import pandas as pd
from pyxirr import xirr

# Define the date range for the data
end_date = datetime.now()
start_date = end_date - timedelta(days=700)

# define buy and sell factors
BUY_FACTOR = 0.04
SELL_FACTOR = 0.07

# Define the stock ticker symbols
#tickers = ['RELIANCE.NS', 'INFY.NS', 'BAJFINANCE.NS', 'HINDUNILVR.NS']
tickers = ['RELIANCE.NS']

def get_stock_data(ticker, start_date, end_date):
    """Retrieve historical data for candle starting at 2.15 PM."""
    data = yf.download(ticker, start=start_date, end=end_date, interval="1h")
    time = "14:15:00"
    data = data[data.index.time == pd.to_datetime(time).time()]
    return data.reset_index()

for ticker in tickers:
    data = get_stock_data(ticker, start_date, end_date)
    # Initializing varibales considering 1st buy on 1st day.
    closed_price_data = list(zip(data['Close'].round(2), data['Datetime'].dt.date))
    initial_buy = closed_price_data[0][0]
    initial_date = closed_price_data[0][1]
    buy_level =[initial_buy]
    buy_reference = buy_level[-1]
    corresponding_sell_level =[initial_buy+ initial_buy*SELL_FACTOR]
    sell_reference = corresponding_sell_level[-1]
    Executed_sell_values=[]
    Executed_buy_values =[]
    all_transactions = ['B']
    all_buy_prices = [initial_buy]
    all_sell_prices = [initial_buy+ initial_buy*SELL_FACTOR]
    xirr_df = pd.DataFrame(columns = ["date","value"])
    xirr_df = xirr_df.append({"date":initial_date, "value":-initial_buy}, ignore_index = True)
    final_date = closed_price_data[-1][1]
    final_price = closed_price_data[-1][0]

    def handle_buy_trans(cur_val, cur_date, last_open_buy, xirr_df):
        xirr_df = xirr_df.append({"date":cur_date, "value":-cur_val}, ignore_index = True)
        buy_level.append(cur_val)
        all_buy_prices.append(cur_val)
        all_transactions.append('B')
        corresponding_sell_level.append(cur_val+(SELL_FACTOR*cur_val))
        all_sell_prices.append(cur_val+(SELL_FACTOR*cur_val))
        buy_reference = buy_level[-1]
        sell_reference = corresponding_sell_level[-1]
        return buy_reference, sell_reference, xirr_df



    for val_date in closed_price_data[1:]:
        cur_val = val_date[0]
        cur_date = val_date[1]
        last_open_buy =  buy_level[-1] if len(buy_level) > 0 else None

        #handles buy logic if current price is less than 4% of reference buy value and 2.5% less than last buy if available.
        if cur_val < buy_reference-(BUY_FACTOR*buy_reference) and (last_open_buy is None or cur_val < last_open_buy-0.025*last_open_buy):
            buy_reference, sell_reference, xirr_df = handle_buy_trans(cur_val, cur_date, last_open_buy, xirr_df)

        elif len(corresponding_sell_level)>0:
            #handles sell logic if current price is greater than reference sell value.
            if cur_val > sell_reference:
                corresponding_sell_level.pop()
                Executed_buy_values.append(buy_level.pop())
                all_transactions.append('S')
                Executed_sell_values.append(cur_val)
                xirr_df = xirr_df.append({"date":cur_date, "value":cur_val}, ignore_index = True)
                if len(buy_level) > 0:
                    sell_reference = corresponding_sell_level[-1]
                    buy_reference = cur_val
                else:
                    buy_reference = cur_val
        else:
            if cur_val > buy_reference:
                buy_reference = cur_val

    number_of_pending_sale_trans = len(buy_level)
    cur_val_of_pending_trans = number_of_pending_sale_trans*final_price
    
    invested_in_pending_trans = sum(buy_level)
    current_absolute_profit = sum(Executed_sell_values) - sum(Executed_buy_values) + cur_val_of_pending_trans - invested_in_pending_trans

    xirr_df = xirr_df.append({"date":final_date, "value":cur_val_of_pending_trans}, ignore_index = True)
    print(xirr_df)
    # get maximum number of open buy transactions.
    count = 0
    max_count = 0
    for i in all_transactions:
        if i == 'B':
            count=count+1
        else: 
            count=count-1 
        max_count = max(max_count, count)

    print('\n---------------------------*****-----------------------------\n')
    print(f"Data for {ticker}")
    xirr = xirr(xirr_df['date'], xirr_df['value'])
    print(f"current absolute profit considering 1 share:{current_absolute_profit}")
    print(f"xirr: {xirr}")
    print(f"Max number of open Buys at some point of time :{max_count}")
    print('\n---------------------------*****-----------------------------\n')
    print(f"all buy values:{all_buy_prices}")
    print(f"all sell values:{all_sell_prices}")
    print('\n---------------------------*****-----------------------------\n')
    print(f"Pending sell Orders:{corresponding_sell_level}")
    print(f"Corresponding buy Orders:{buy_level}")
    print('\n---------------------------*****-----------------------------\n')
    print(f"Executed Sell Orders:{Executed_sell_values[::-1]}")
    print(f"Corresponding Executed Buy orders:{Executed_buy_values[::-1]}")
    print('\n---------------------------*****-----------------------------\n')
    print(f"all_transactions in sequence :{all_transactions}")
    print(f"Count of Sell Orders :{all_transactions.count('S')}")
    print(f"Count of Buy Orders :{all_transactions.count('B')}")
    




