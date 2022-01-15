import os


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'sulertia'
    LOCAL_DB = os.environ.get('LOCAL_PG','')
    SQLALCHEMY_DATABASE_URI = LOCAL_DB or os.environ.get('DATABASE_URL', '').replace(
        'postgres://', 'postgresql://') \
        or 'sqlite:///bot/database.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

