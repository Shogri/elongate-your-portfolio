from investopedia_simulator_api.investopedia_api import InvestopediaApi, TradeExceedsMaxSharesException
import json
import datetime

# sys.path.append('./investopedia_simulator_api')



credentials = {}
with open('credentials.json') as ifh:
    credentials = json.load(ifh)
# look at credentials_example.json
# credentials = {"username": "you@example.org", "password": "yourpassword" }
client = InvestopediaApi(credentials)

p = client.portfolio

print("account value: %s" % p.account_value)
print("cash: %s" % p.cash)
print("buying power: %s" % p.buying_power)
print("annual return pct: %s" % p.annual_return_pct)



# Read your portfolio
long_positions = client.portfolio.stock_portfolio
short_positions = client.portfolio.short_portfolio
my_options = client.portfolio.option_portfolio

for pos in long_positions:
    print("--------------------")
    print(pos.symbol)
    print(pos.purchase_price)
    print(pos.current_price)
    print(pos.change)
    print(pos.total_value)

    # This gets a quote with addtional info like volume
    quote = pos.quote
    if quote is not None:
        print(quote.__dict__)
    print("---------------------")


# construct a trade (see trade_common.py and stock_trade.py for a hint)
trade1 = client.StockTrade(symbol='GOOG', quantity=10, trade_type='buy',
                           order_type='market', duration='good_till_cancelled', send_email=True)
# validate the trade
trade_info = trade1.validate()
print(trade_info)

# change the trade to a day order
trade1.duration = 'day_order'
# Another way to change the trade to a day order
trade1.duration = client.TradeProperties.Duration.DAY_ORDER()

# make it a limit order
trade1.order_type = 'limit 20.00'
# alternate way
trade1.order_type = client.TradeProperties.OrderType.LIMIT(20.00)

# validate it, see changes:
trade_info = trade1.validate()
if trade1.validated:
    print(trade_info)
    trade1.execute()

# View open orders / pending trades
client.refresh_portfolio()
open_orders = client.open_orders


client.refresh_portfolio()
