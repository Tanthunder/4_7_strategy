import yfinance as yf
from datetime import datetime, timedelta
import pandas as pd
import mysql.connector
import smtplib

def send_mail(sell_reference=0, buy_reference=0,flag='default'):
    """Send mails."""
    buy_price = buy_reference
    sell_price = sell_reference
    flg = flag
    sender_email = "xxx"
    receiver_email = "xxx"
    password = "xxxx"
    message1 = f"""Subject: Buy alert for Reliance from Tanthunder.


    Buy Reliance shares at or below {buy_price}.
    Its corresponding sell price will be higher than {sell_price}.
    """

    message2 = f"""Subject: Sell alert for Reliance from Tanthunder.


    Sell Reliance shares at or above {sell_price}."""
    
    message3 = f"""Subject: Price alert for Reliance from Tanthunder.


    No action required for Reliance shares.
    Market price of Reliance is {sell_price}"""

    message4 = f"""Subject: Error encountered.


    Technical Error encountered while fetching data.
    Issue is most prabably due to failed API call."""


    if flg == 'buy':
        message = message1
    elif flg == 'sell':
        message = message2
    elif flg == 'error':
        message = message4
    else:
        message = message3

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(sender_email, password)
    server.sendmail(sender_email, receiver_email, message)
    server.quit()

cnx = mysql.connector.connect(user='xxx',
                              password='xxxx',
                              host='xxx',
                              database='xxx')

#Creating a cursor object using the cursor() method
cursor = cnx.cursor()

def get_buy_sell_ref():
    "Retrive reference values for Buy and Sell."
    cursor.execute("select * from reference")
    op = cursor.fetchall()[0]
    buy_reference = op[1]
    sell_reference = op[2]
    return(buy_reference,sell_reference)

end_date = datetime.now()
start_date = end_date - timedelta(days=700)
mail_sent = False
ticker = "RELIANCE.NS"
try:
    stock_data = yf.Ticker(ticker).info
    current_price = stock_data["regularMarketPrice"]
except:
    try:
        data = yf.download(ticker, start=start_date, end=end_date, interval="1h")
        time = "13:15:00" 
        data = data[data.index.time == pd.to_datetime(time).time()]
        datalist = data['Adj Close'].tolist()
        adj_close_data = [round(i,2) for i in datalist]
        current_price = adj_close_data[0]
    except:
        send_mail(flag='error')
    


print(current_price)
cursor.execute("SELECT buy_ref FROM reference;")
buy_reference = cursor.fetchall()[0][0]

if current_price < buy_reference-(0.04*buy_reference):
    #buy shares
    buy_reference = current_price
    sell_reference = current_price + 0.08*current_price
    #update buy reference in table
    cursor.execute(f"UPDATE reference SET buy_ref = {buy_reference}, sell_ref = {sell_reference};")
    cnx.commit()
    cursor.execute(f"INSERT INTO buy_sell_prices (buy_value, sell_value, is_sell) values ({buy_reference}, {sell_reference}, FALSE);")
    cnx.commit()
    send_mail(sell_reference,buy_reference,'buy')
    mail_sent = True

cursor.execute("SELECT EXISTS (SELECT * FROM buy_sell_prices WHERE is_sell = FALSE);")
not_empty = cursor.fetchone()[0]

if not_empty:
    #fetch sell ref
    cursor.execute("SELECT buy_ref, sell_ref FROM reference;")
    dat = cursor.fetchall()[0]

    buy_ref = dat[0]
    sell_reference = dat[1]
    
    if current_price > sell_reference:
        #sell shares
        send_mail(sell_reference,flag='sell')
        mail_sent = True
        #set is sell flag to 1
        cursor.execute(f"UPDATE buy_sell_prices SET is_sell = TRUE WHERE sell_value like '%{sell_reference}%';")
        cnx.commit()

        cursor.execute("SELECT EXISTS (SELECT * FROM buy_sell_prices WHERE is_sell = FALSE);")
        available= cursor.fetchone()[0]
        
        if available:

            cursor.execute("SELECT buy_value, sell_value FROM buy_sell_prices WHERE is_sell = FALSE ORDER BY id DESC LIMIT 1;")

            data = cursor.fetchall()[0]
            
            buy_value = data[0]
            sell_value = data[1]
            cursor.execute(f"UPDATE reference SET buy_ref = {current_price}, sell_ref ={sell_value};")
            cnx.commit()
            #cursor.execute(f"UPDATE reference SET buy_ref = {current_price};")

        else:
            cursor.execute(f"UPDATE reference SET buy_ref ={current_price};")
            cnx.commit()

else :
    if current_price > buy_reference:
        cursor.execute(f"UPDATE reference SET buy_ref = {current_price};")
        cnx.commit()

if not mail_sent:
    send_mail(sell_reference=current_price)

print('success')

cursor.close()
cnx.close()

