from investopedia_simulator_api.api_models import Portfolio
from investopedia_simulator_api.parsers import Parsers, option_lookup, stock_quote
from investopedia_simulator_api.trade_common import Duration, OrderType, TradeType, Trade
from investopedia_simulator_api.trade_common import TradeExceedsMaxSharesException, TradeNotValidatedException, InvalidOrderDurationException, InvalidOrderTypeException, InvalidTradeTypeException
from investopedia_simulator_api.option_trade import OptionTrade
from investopedia_simulator_api.stock_trade import StockTrade
from investopedia_simulator_api.session_singleton import Session
from investopedia_simulator_api.utils import TaskQueue, validate_and_execute_trade


class InvestopediaApi(object):
    def __init__(self, credentials):
        Session.login(credentials)
        self.portfolio = Parsers.get_portfolio()
        self.open_orders = self.portfolio.open_orders

    class TradeQueue(TaskQueue):
        def __init__(self):
            super().__init__(default_task_function=validate_and_execute_trade)


    class StockTrade(StockTrade):
        pass

    class OptionTrade(OptionTrade):
        pass

    class TradeProperties:
        class Duration(Duration):
            pass

        class OrderType(OrderType):
            pass

        class TradeType(TradeType):
            pass

    @staticmethod
    def get_option_chain(symbol, strike_price_proximity=3):
        return option_lookup(symbol, strike_price_proximity=strike_price_proximity)

    @staticmethod
    def get_stock_quote(symbol):
        return stock_quote(symbol)

    def refresh_portfolio(self):
        self.portfolio = Parsers.get_portfolio()
        self.open_orders = self.portfolio.open_orders