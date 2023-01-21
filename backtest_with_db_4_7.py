import yfinance as yf
from datetime import datetime, timedelta
import pandas as pd
from utils import get_buy_sell_ref, get_current_market_price
from connection import cursor
import time as ts

end_date = datetime.now()
start_date = end_date - timedelta(days=700)

ticker = 'Reliance.NS'

data = yf.download(ticker, start=start_date, end=end_date, interval="1h")

time = "14:15:00" 
data = data[data.index.time == pd.to_datetime(time).time()]

datalist = data['Adj Close'].tolist()
adj_close_data = [round(i,2) for i in datalist]

abuy = []
asell = []

buy_reference,sell_reference = get_buy_sell_ref()

for i in adj_close_data[1:]:
    current_price = i

    cursor.execute("SELECT buy_ref FROM reference;")
    buy_reference = cursor.fetchall()[0][0]
    print(f"buyyyyy: {buy_reference}")
    
    if current_price < buy_reference-(0.04*buy_reference):
        #buy shares
        abuy.append(current_price)
        asell.append(current_price + 0.08*current_price)
        buy_reference = current_price
        sell_reference = current_price + 0.08*current_price
        #update buy reference in table
        cursor.execute(f"UPDATE reference SET buy_ref = {buy_reference}, sell_ref = {sell_reference};")
        cursor.execute(f"INSERT INTO buy_sell_prices (buy_value, sell_value, is_sell) values ({buy_reference}, {sell_reference}, FALSE);")
    
    cursor.execute(f"SELECT EXISTS (SELECT * FROM buy_sell_prices WHERE is_sell = FALSE);")
    not_empty = cursor.fetchone()[0]

    if not_empty:
        #fetch sell ref
        cursor.execute("SELECT sell_ref FROM reference;")
        sell_reference = cursor.fetchall()[0][0]
        print(f"selllllll: {sell_reference}")

        if current_price > sell_reference:
            #sell shares
            #set is sell flag to 1
            cursor.execute(f"UPDATE buy_sell_prices SET is_sell = TRUE WHERE sell_value = {sell_reference};")
            
            cursor.execute(f"SELECT EXISTS (SELECT * FROM buy_sell_prices WHERE is_sell = FALSE);")
            available= cursor.fetchone()[0]
            print(available)

            if available:
                
                cursor.execute(f"SELECT buy_value, sell_value FROM buy_sell_prices WHERE is_sell = FALSE ORDER BY id DESC LIMIT 1;")
                data = cursor.fetchall()[0]
                print(data)
                
                buy_value = data[0]
                sell_value = data[1]
                print(buy_value,sell_value,current_price,sell_reference)
                cursor.execute(f"UPDATE reference SET buy_ref = {current_price}, sell_ref ={sell_value};")
                #cursor.execute(f"UPDATE reference SET buy_ref = {current_price};")

            else:
                cursor.execute(f"UPDATE reference SET buy_ref ={current_price};")
                

        #need to think if this required
        #elif current_price > 1.02*buy_reference:
            #cursor.execute(f"UPDATE reference SET buy_ref ={current_price};")

            '''
            if current_price > buy_value + (0.05*buy_value):
                buy_reference = current_price
                cursor.execute(f"UPDATE reference SET buy_ref = {buy_reference};")
            '''
    else :
        if current_price > buy_reference:
            cursor.execute(f"UPDATE reference SET buy_ref = {current_price};")
            

print(abuy)
print(asell)
print('success')

