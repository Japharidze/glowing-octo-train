from flask import make_response, request
from flask import current_app as app

from .bot import run_bot
from .models import Coin, TradePair
from .bot.crud import insert_coin, update_coin, insert_tp, insert_trade

@app.route('/')
def index():
    return make_response('; '.join([str(x) for x in Coin.query.all()]), 200)

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
    run_bot()
    return make_response('Bot started successfuly!', 200)
