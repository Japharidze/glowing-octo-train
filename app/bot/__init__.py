import time

from .Data.DataStream import BinanceDataStream
from .Action.KuCoinTrade import MarketAction
from .Data.KucoinSymbols import load_kucoin_binance_symbols
from .helper import load_config_file
from app.bot.crud import get_coins  # TODO: change to relative path

def run_bot():
    config_path = 'app/bot/config_GR.json'
    config = load_config_file(config_path)

    # TODO: change info to something more robust for accessing threads
    info = dict()

    coin_list = get_coins()
    print("Total Symbols in the list: ", len(coin_list))

    for coin in coin_list:
        try:
            if coin.allow_trade:
                stream = BinanceDataStream(config, coin)
                stream.start()

                actions = MarketAction(stream, config, coin)
                actions.start()
                info[coin.kucoin_name] = {'stream': stream, 'actions': actions}
        except Exception as e:
            print(e)
