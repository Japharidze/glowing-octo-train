import time

from .Data.DataStream import BinanceDataStream
from .Action.KuCoinTrade import MarketAction
from .Data.KucoinSymbols import load_kucoin_binance_symbols
from .helper import load_config_file
from app.bot.crud import get_coins  # TODO: change to relative path

def run_bot():
    config_path = 'app/bot/config_GR.json'
    config = load_config_file(config_path)
    # symbol_csv = load_kucoin_binance_symbols(config)

    # TODO: change info to something more robust for accessing threads
    info = dict()

    coin_list = get_coins()
    print("Total Symbols in the list: ", len(coin_list))

    for coin in coin_list:
        try:
            if coin.allow_trade:
                config['symbol'] = coin.binance_name  # Set different symbols
                stream = BinanceDataStream(config)
                stream.start()

                time.sleep(5)
                config['symbol'] = coin.kucoin_name  # Set different symbols
                bought_id = coin.bought_id
                actions = MarketAction(stream, config, bought_id)
                actions.start()
                info[coin.kucoin_name] = {'stream': stream, 'actions': actions}
        except Exception as e:
            print(e)
