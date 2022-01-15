from app.models import Coin, Trade, TradePair
from app import db

def insert_coin(**kwargs):
    cn = Coin(**kwargs)
    db.session.add(cn)
    db.session.commit()

def insert_trade(**kwargs):
    trade = Trade(**kwargs)
    db.session.add(trade)
    db.session.commit()

def insert_tp(**kwargs):
    tp = TradePair(**kwargs)
    db.session.add(tp)
    db.session.commit()

def get_coins():
    return Coin.query.all()

def get_trades():
    return Trade.query.all()

def update_coin(trade_id: str, kucoin_name: str):
    Coin.query.filter_by(kucoin_name=kucoin_name).\
        update({'bought_id': trade_id})
    db.session.commit()

def clear_db():
    db.session.query(Trade).delete()
    db.session.query(TradePair).delete()
    db.session.commit()
