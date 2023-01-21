from connection import cursor
import yfinance as yf


def get_buy_sell_ref():
    "Retrive reference values for Buy and Sell."
    cursor.execute("select * from reference")
    op = cursor.fetchall()[0]
    buy_reference = op[1]
    sell_reference = op[2]
    return(buy_reference,sell_reference)

def get_current_market_price(ticker):
    "fetch current stock price."
    info = yf.Ticker(ticker).info
    current_price = info
    return(current_price)
