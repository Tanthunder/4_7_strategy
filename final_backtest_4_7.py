import yfinance as yf
from datetime import datetime, timedelta
import pandas as pd

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

    # Considering data at 2:15 PM only.
    time = "14:15:00" 
    data = data[data.index.time == pd.to_datetime(time).time()]

    # Considering adjusted close price and converting to list , rounding to 2 decimal places.
    datalist = data['Adj Close'].tolist()
    adj_close_data = [round(i,2) for i in datalist]
    
    initial_buy = adj_close_data[0]
    buy_level =[initial_buy]
    buy_ref = buy_level[-1]
    corresponding_sell_level =[initial_buy+ initial_buy*SELL_FACTOR]
    sell_ref = corresponding_sell_level[-1]
    Sell_values=[]
    Buy_values =[]
    transactions = ['B']
    all_buys = [initial_buy]
    all_sells = [initial_buy+ initial_buy*SELL_FACTOR]

    #looping through the adj close values
    for cur_val in adj_close_data[1:]:
        #handles buy logic if current price is less than 4% of reference buy value.
        if cur_val < buy_ref-(BUY_FACTOR*buy_ref):
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
    

    initial_investment = all_buys[0]
    final_value = adj_close_data[-1]
    cash_flows = sum(Sell_values)-sum(Buy_values[1:])
    total_return = (final_value - initial_investment + cash_flows) / initial_investment * 100
    
    print(f"Data for {ticker}")
    print('\n---------------------------*****-----------------------------\n')
    print(f"all buy values:{all_buys}")
    print(f"all sell values:{all_sells}")
    print('\n---------------------------*****-----------------------------\n')
    print(f"Pending sell Orders:{corresponding_sell_level}")
    print(f"Corresponding buy Orders:{buy_level}")
    print('\n---------------------------*****-----------------------------\n')
    print(f"Executed Sell Orders:{Sell_values[::-1]}")
    print(f"Corresponding Buy orders:{Buy_values[::-1]}")
    print('\n---------------------------*****-----------------------------\n')
    print(f"Transactions in sequence :{transactions}")
    print(f"Count of Sell Orders :{transactions.count('S')}")
    print(f"Count of Buy Orders :{transactions.count('B')}")
    print('\n---------------------------*****-----------------------------\n')
    
    print(f"Overall Profit Amount: {sum(Sell_values)-sum(Buy_values)}")
    print(f"Approximate return % : {total_return}%")




