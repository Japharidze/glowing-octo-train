import logging
import time
from decimal import Decimal

from threading import Thread

from kucoin.client import Trade, Market, User
from app.bot.Data.KucoinSymbols import load_kucoin_binance_symbols
from app.bot.crud import insert_trade, insert_tp, update_coin


class MarketAction(Thread):
    user = None
    market = None
    client = None
    api_key = ''
    api_secret = ''
    api_passphrase = ''

    start_balance = None
    allow_trade = True
    config = None

    def __init__(self, stream, config, buy_order_id=''):
        Thread.__init__(self)
        MarketAction.init_class_variables(config)

        self.symbol = config['symbol']
        self.funds = config['funds']
        self.stream = stream
        self.coef = config['coef']
        self.window = config['window']

        self.quoteIncrement = self.calculate_increment()  # TODO: correct precision
        self.order_ids = []
        self.buy_order_id = ''
        self.trade_amount = ''
        self.initialize_trade_info(buy_order_id)

        self.stop = False

    def run(self):
        while not self.stop:
            if self.stream.check_for_action:
                # print(f'Action -> Checking for action! {self.symbol}')
                if self.indicator_buy() and self.allow_trade and \
                        not self.indicator_sell() and not self.buy_order_id:
                    self.create_order('buy', funds=self.funds)

                elif self.indicator_sell() and self.buy_order_id:
                    self.create_order('sell', size=self.trade_amount)

                self.stream.check_for_action = False
            # os.system('cls' if os.name == 'nt' else 'clear')

            time.sleep(0.5)
        print('Action Thread Stopped!')

    def indicator_buy(self):
        good_trend = self.stream.data['EMA50'].rolling(window=60).apply(
            lambda x: (x[-1] - x[0]) / x[0] > -10e-3).fillna(0)

        up_candles = self.stream.data['HA_Close'] > self.stream.data['HA_Open']
        try:  # see if Trades are available
            indicator = (self.stream.data['Volume'] > self.coef * self.stream.data['EMA60_Volume']) * (
                    self.stream.data['Trades'] > self.coef * self.stream.data['EMA60_Trades'])
        except Exception:
            indicator = self.stream.data['Volume'] > self.coef * self.stream.data['EMA60_Volume']

        indicator *= good_trend * up_candles
        buy = indicator.iloc[-self.window:].sum() == self.window
        #         indicator = indicator.rolling(window=window).apply(lambda x: np.sum(x) >= window).fillna(0)
        return buy

    def indicator_sell(self):
        lose_momentum = self.stream.data['HA_Close_slow'].iloc[-1] < self.stream.data['HA_Open_slow'].iloc[-1]
        if lose_momentum:
            return True
        return False

    def create_order(self, side, **kwargs):
        try:
            order_id = self.client.create_market_order(self.symbol, side, **kwargs).get('orderId')
            self.order_ids.append(order_id)
            logging.info(f'{side}, symbol: {self.symbol}, order_id: {order_id}')
            print(f'{side} {self.symbol}, order_id: {order_id}')
        except Exception as e:
            message = f'Exception (in create_order): {side} {self.symbol} {e}'
            print(message)
            logging.warning(message)
        else:
            if side == 'buy':
                while True:  # wait for order to fill
                    order_data = self.client.get_order_details(order_id)
                    if not order_data.get('isActive'):
                        trade_amount = order_data.get('dealSize')
                        self.trade_amount = self.round_trade_amount(trade_amount, self.quoteIncrement)
                        break
                    time.sleep(0.5)
                self.buy_order_id = order_id
                # update_coin()
                # insert_trade()
            elif side == 'sell':
                # update_coin()
                # insert_trade()
                # insert_tp()
                logging.info(f'Trade Complete! Symbol: {self.symbol}, pair_order_ids: buy: {self.buy_order_id}, sell: {order_id}')
                self.buy_order_id = ''
                self.trade_amount = '0'
                self.update_trade_allowance()

            self.save_trade_in_csv(self.symbol, self.buy_order_id)

    def calculate_increment(self):
        increments = {data.get('symbol'): data.get('quoteIncrement') for data in self.market.get_symbol_list()}
        return increments.get(self.symbol)

    def initialize_trade_info(self, buy_order_id):
        try:
            order_data = self.client.get_order_details(buy_order_id)
            if not order_data.get('isActive'):
                trade_amount = order_data.get('dealSize')
                trade_amount = self.round_trade_amount(trade_amount, self.quoteIncrement)
            else:  # if is not bought make trade amount empty string
                trade_amount = ''
        except Exception as e:
            self.buy_order_id = ''
            self.trade_amount = '0'
            message = f'Exception in loading Trade info from CSV for {self.symbol}: {e}'
            if '400100' not in str(e):  # if different error than: 'order not exist'
                print(message)
                logging.warning(message)
        else:
            if trade_amount:
                self.buy_order_id = buy_order_id
                self.trade_amount = trade_amount

    @classmethod
    def save_trade_in_csv(cls, symbol, buy_order_id):
        try:
            symbol_csv = load_kucoin_binance_symbols(cls.config)
            symbol_csv.at[symbol_csv.Kucoin == symbol, 'Bought_ID'] = buy_order_id
            symbol_csv.to_csv(cls.config['symbol_csv_path'], index=False)
            # print("Trade id saved in CSV!")
        except Exception as e:
            message = f'Exception in Saving trade ID for {symbol} in CSV: {e}'
            print(message)
            logging.warning(message)

    @staticmethod
    def round_trade_amount(funds, increment):
        # use maximum of '0.0001' and value returned from Kucoin as values got from Kucoin are incorrect 
        increment = max(increment, '0.0001')
        return str(Decimal(funds).quantize(Decimal(increment), rounding='ROUND_DOWN'))

    @classmethod
    def sell_everything(cls, quote='USDT', account_type='trade'):
        price_dict = dict()
        for data in cls.market.get_all_tickers().get('ticker'):
            symbol = data.get('symbol')
            price_dict[symbol] = float(data.get('sell'))

        account_balance = cls.user.get_account_list(account_type=account_type)
        for data in account_balance:
            currency = data.get('currency')
            if currency != quote:
                if f'{currency}-{quote}' in price_dict.keys():
                    symbol = f'{currency}-{quote}'
                    price = price_dict[symbol]
                    balance = float(data.get('balance')) * price
                    if balance > 5:
                        cls.client.create_market_order(symbol, 'sell', funds=cls.round_trade_amount(balance, '0.001'))
                        print(f'Sold {symbol}')
                elif f'{quote}-{currency}' in price_dict.keys():
                    symbol = f'{quote}-{currency}'
                    price = price_dict[symbol]
                    balance = float(data.get('balance')) / price
                    if balance > 5:
                        cls.client.create_market_order(symbol, 'buy', size=cls.round_trade_amount(balance, '0.001'))
                        print(f'Sold {symbol}')

                cls.save_trade_in_csv(symbol, '')

        print('Done Selling!')

    @classmethod
    def calculate_total_balance(cls, quote='USDT', account_type='trade'):
        price_dict = dict()
        for data in cls.market.get_all_tickers().get('ticker'):
            symbol = data.get('symbol')
            price_dict[symbol] = float(data.get('sell'))

        account_balance = cls.user.get_account_list(account_type=account_type)
        balance = 0
        for data in account_balance:
            currency = data.get('currency')
            if currency != quote:
                if f'{currency}-{quote}' in price_dict.keys():
                    price = price_dict[f'{currency}-{quote}']
                    balance += float(data.get('balance')) * price
                elif f'{quote}-{currency}' in price_dict.keys():
                    price = price_dict[f'{quote}-{currency}']
                    balance += float(data.get('balance')) / price
            else:
                balance += float(data.get('balance'))
        message = f'Total Balance is {balance}'
        logging.info(message)
        return balance

    @classmethod
    def update_trade_allowance(cls):
        """check if balance is not very low to allow further trading"""
        cls.allow_trade = cls.calculate_total_balance() > cls.start_balance * 0.8
        # TODO: change allow_trade coefficient to be included in config file

    @classmethod
    def init_class_variables(cls, config):
        """Initialize class variables on the first time"""
        if not MarketAction.user:
            cls.api_key = config['api_key']
            cls.api_secret = config['api_secret']
            cls.api_passphrase = config['api_passphrase']
            cls.user = User(cls.api_key, cls.api_secret, cls.api_passphrase)
            cls.market = Market(cls.api_key, cls.api_secret, cls.api_passphrase)
            cls.client = Trade(cls.api_key, cls.api_secret, cls.api_passphrase)

            cls.start_balance = cls.calculate_total_balance()
            cls.config = config
            print('MarketAction Class Variables Successfully Initialized!')