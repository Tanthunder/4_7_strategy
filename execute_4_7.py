from utils import get_buy_sell_ref, get_current_market_price
from connection import cursor

TICKER = 'tcs.NS'

buy_reference,sell_reference = get_buy_sell_ref()

#current_price = get_current_market_price(TICKER)
current_price = 100

cursor.execute(f"SELECT EXISTS (SELECT * FROM buy_sell_prices WHERE is_sell = FALSE);")
not_empty = cursor.fetchone()[0]

if current_price < buy_reference-(0.04*buy_reference):
    #buy shares
    buy_reference = current_price
    sell_reference = current_price + 0.07*current_price
    #update buy reference in table
    cursor.execute(f"UPDATE reference SET buy_ref = {buy_reference}, sell_ref = {sell_reference};")
    cursor.execute(f"INSERT INTO buy_sell_prices (buy_value,sell_value,is_sell) values ({buy_reference},{sell_reference},FALSE);")

if not_empty:

    if current_price > sell_reference:
        #sell shares
        #set is sell flag to 1
        cursor.execute(f"UPDATE buy_sell_prices SET Is_sell = TRUE WHERE sell_value = {sell_reference};")
        
        cursor.execute(f"SELECT EXISTS (SELECT * FROM buy_sell_prices WHERE is_sell = FALSE);")
        available= cursor.fetchone()[0]
        print(available)

        if available:
            cursor.execute(f"SELECT buy_value, sell_value FROM buy_sell_prices WHERE Is_sell = FALSE ORDER BY id DESC LIMIT 1;")
            data = cursor.fetchall()[0]
            print(data)
            buy_value = data[0]
            sell_value = data[1]
            print(buy_value,sell_value)

            cursor.execute(f"UPDATE reference SET sell_ref ={sell_value};")
            cursor.execute(f"UPDATE reference SET buy_ref = {current_price};")

        else:
            cursor.execute(f"UPDATE reference SET buy_ref ={current_price};")

    #need to think if this required
    elif current_price > 1.04*buy_reference and current_price < 1.07*buy_reference:
        cursor.execute(f"UPDATE reference SET buy_ref ={current_price};")

        '''
        if current_price > buy_value + (0.05*buy_value):
            buy_reference = current_price
            cursor.execute(f"UPDATE reference SET buy_ref = {buy_reference};")
        '''
else :
    if current_price > buy_reference:
        cursor.execute(f"UPDATE reference SET buy_ref = {current_price};")









