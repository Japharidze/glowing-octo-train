import time

from .Data.DataStream import BinanceDataStream
from .Action.KuCoinTrade import MarketAction
from .Data.KucoinSymbols import load_kucoin_binance_symbols
from .helper import load_config_file


def run_bot():
    config_path = 'app/bot/config_GR.json'

    config = load_config_file(config_path)
    symbol_csv = load_kucoin_binance_symbols(config)

    for _, row in symbol_csv.iterrows():
        try:
            binance_symbol = row['Binance']
            kucoin_symbol = row['Kucoin']
            symbol_bought_ID = row['Bought_ID']

            config['symbol'] = binance_symbol  # Set different symbols
            stream = BinanceDataStream(config)
            stream.start()

            time.sleep(5)
            config['symbol'] = kucoin_symbol  # Set different symbols
            actions = MarketAction(stream, config, symbol_bought_ID)
            actions.start()
        except Exception as e:
            print(e)
