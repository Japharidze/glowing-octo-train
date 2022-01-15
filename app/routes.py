from threading import Thread

from flask import make_response, request
from flask import current_app as app

from .bot import run_bot
from .models import Coin, TradePair, Trade
from .bot.crud import insert_coin, update_coin, insert_tp, insert_trade, clear_db, get_trades

@app.route('/')
def index():
    return make_response('; '.join([str(x) for x in Coin.query.all()]), 200)

@app.route('/list_trades')
def list_trades():
    return make_response('; '.join([str(x) for x in get_trades()]))


@app.route('/insert_coins')
def insert_coins():
    coins = request.get_json().get('coins')
    for coin in coins:
        insert_coin(**coin)
    return make_response('SDA', 200)

@app.route('/test_update')
def update_c():
    update_coin('','ADA-USDT')
    return make_response('SDA', 200)

@app.route('/list_tps')
def list_tps():
    return make_response('; '.join([str(x) for x in TradePair.query.all()]), 200)

@app.route('/insert_tp')
def insert_pt():
    coins = request.get_json().get('items')
    for coin in coins:
        insert_trade(**coin)
    return make_response('SDA', 200)

@app.route('/init_bot')
def init_bot():
    t1 = Thread(target=run_bot, daemon=True)
    t1.start()
    return make_response('Bot started successfuly!', 200)

############# TEST ############


@app.route('/backtest')
def backtest_bot():
    run_bot(mode='backtest')
    return make_response('Backtest Run !', 200)

@app.route('/clear_trades_from_db')
def clear_trades():
    clear_db()
    return make_response('; '.join([str(x) for x in Trade.query.all()]), 200)


from .bot.Action.KuCoinTrade import MarketAction
from .bot.helper import load_config_file
import time

@app.route('/test_buy_sell')
def test_buy_sell():
    config_path = 'app/bot/config_GR.json'
    config = load_config_file(config_path)
    config['mode'] = 'live'
    for coin in Coin.query.all():
        try:
            actions = MarketAction('', config, coin)
            actions.create_order('buy', funds=10)
            time.sleep(1)
            actions.create_order('sell', size=actions.trade_amount)
        except Exception as e:
            print(coin, e)
        break
    return make_response('; '.join([str(x) for x in Trade.query.all()]), 200)

