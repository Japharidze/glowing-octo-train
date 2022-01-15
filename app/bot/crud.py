from sqlalchemy.orm import sessionmaker

from app.models import Coin, Trade, TradePair
from app import db

Session = sessionmaker(bind=db.engine)

def insert_coin(**kwargs):
    with Session() as s:
        cn = Coin(**kwargs)
        s.add(cn)
        s.commit()

def insert_trade(**kwargs):
    with Session() as s:
        trade = Trade(**kwargs)
        s.add(trade)
        s.commit()

def insert_tp(**kwargs):
    with Session() as s:
        tp = TradePair(**kwargs)
        s.add(tp)
        s.commit()

def get_coins():
    with Session() as s:
        res = s.query(Coin).all()
    return res

def get_trades():
    with Session() as s:
        res = s.query(Trade).all()
    return res

def update_coin(trade_id: str, kucoin_name: str):
    with Session() as s:
        s.query(Coin).filter_by(kucoin_name=kucoin_name).\
            update({'bought_id': trade_id})
        s.commit()

def clear_db():
    db.session.query(Trade).delete()
    db.session.query(TradePair).delete()
    db.session.commit()
