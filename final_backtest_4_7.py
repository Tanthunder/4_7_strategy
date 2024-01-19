import yfinance as yf
from datetime import datetime, timedelta
import pandas as pd
from pyxirr import xirr

# Define the date range for the data
end_date = datetime.now()
start_date = end_date - timedelta(days=700)

BUY_FACTOR = 0.04
SELL_FACTOR = 0.07

# Define the stock ticker symbol
#tickers = ['RELIANCE.NS', 'INFY.NS', 'BAJFINANCE.NS', 'HINDUNILVR.NS']
tickers = ['RELIANCE.NS']

for ticker in tickers:

    # Retrieve historical intraday data for the stock (timeframe = 1hr)
    data = yf.download(ticker, start=start_date, end=end_date, interval="1h")

    # Considering data at 2:15 PM only. candle starting at 2.15 PM.
    time = "14:15:00" 
    data = data[data.index.time == pd.to_datetime(time).time()]
    data = data.reset_index()
    # Considering close price, date and converting to list , rounding to 2 decimal places.
    close_data = list(zip(data['Close'].round(2), data['Datetime'].dt.date))
    initial_buy = close_data[0][0]
    initial_date = close_data[0][1]
    buy_level =[initial_buy]
    buy_ref = buy_level[-1]
    corresponding_sell_level =[initial_buy+ initial_buy*SELL_FACTOR]
    sell_ref = corresponding_sell_level[-1]
    Sell_values=[]
    Buy_values =[]
    transactions = ['B']
    all_buys = [initial_buy]
    all_sells = [initial_buy+ initial_buy*SELL_FACTOR]
    xirr_df = pd.DataFrame(columns = ["date","value"])
    xirr_df = xirr_df.append({"date":initial_date, "value":-initial_buy}, ignore_index = True)
    final_date = close_data[-1][1]
    final_price = close_data[-1][0]

    #looping through the close values
    for val_date in close_data[1:]:
        cur_val = val_date[0]
        cur_date = val_date[1]
        last_open_buy =  buy_level[-1] if len(buy_level) > 0 else 99999

        #handles buy logic if current price is less than 4% of reference buy value.
        if cur_val < buy_ref-(BUY_FACTOR*buy_ref) and  cur_val< last_open_buy-0.02*last_open_buy:
            # handle too close buys
            xirr_df = xirr_df.append({"date":cur_date, "value":-cur_val}, ignore_index = True)
            buy_level.append(cur_val)
            all_buys.append(cur_val)
            transactions.append('B')
            corresponding_sell_level.append(cur_val+(SELL_FACTOR*cur_val))
            all_sells.append(cur_val+(SELL_FACTOR*cur_val))
            buy_ref = buy_level[-1]
            sell_ref = corresponding_sell_level[-1]

        if len(corresponding_sell_level)>0:
            #handles sell logic if current price is greater than reference sell value.
            if cur_val > sell_ref:
                corresponding_sell_level.pop()
                x = buy_level.pop()
                Buy_values.append(x)
                transactions.append('S')
                Sell_values.append(cur_val)
                xirr_df = xirr_df.append({"date":cur_date, "value":cur_val}, ignore_index = True)
                if len(buy_level) > 0:
                    sell_ref = corresponding_sell_level[-1]
                    #buy_ref = cur_val if cur_val > 1.03*buy_level[-1] else buy_level[-1]
                    buy_ref = cur_val
                    
                else:
                    buy_ref = cur_val
                    sell_ref = cur_val + (SELL_FACTOR*cur_val)
            
        else:
            
            if cur_val > buy_ref:
                buy_ref = cur_val
        
        # cont_buys = 0
        # for i in transactions:
        #     if i == 'B':
        #         cont_buys=cont_buys+1
        #     else: 
        #         cont_buys=cont_buys-1 
    

    number_of_pending_sale_trans = len(buy_level)
    cur_val_of_pending_trans = number_of_pending_sale_trans*final_price
    
    invested_in_pending_trans = sum(buy_level)
    current_absolute_profit = sum(Sell_values) - sum(Buy_values) + cur_val_of_pending_trans - invested_in_pending_trans

    xirr_df = xirr_df.append({"date":final_date, "value":cur_val_of_pending_trans}, ignore_index = True)

    count = 0
    max_count = 0
    for i in transactions:
        if i == 'B':
            count=count+1
        else: 
            count=count-1 
        max_count = max(max_count, count)

    xirr = xirr(xirr_df['date'], xirr_df['value'])
    print('\n---------------------------*****-----------------------------\n')
    print(f"Data for {ticker}")
    print(f"current absolute profit considering 1 share:{current_absolute_profit}")
    print(f"xirr: {xirr}")
    print(f"Max number of open Buys :{max_count}")
    print('\n---------------------------*****-----------------------------\n')
    print(f"all buy values:{all_buys}")
    print(f"all sell values:{all_sells}")
    print('\n---------------------------*****-----------------------------\n')
    print(f"Pending sell Orders:{corresponding_sell_level}")
    print(f"Corresponding buy Orders:{buy_level}")
    print('\n---------------------------*****-----------------------------\n')
    print(f"Executed Sell Orders:{Sell_values[::-1]}")
    print(f"Corresponding Executed Buy orders:{Buy_values[::-1]}")
    print('\n---------------------------*****-----------------------------\n')
    print(f"Transactions in sequence :{transactions}")
    print(f"Count of Sell Orders :{transactions.count('S')}")
    print(f"Count of Buy Orders :{transactions.count('B')}")
    




