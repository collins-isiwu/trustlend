import os

class Environment:
    SECRET_KEY = os.environ.get('SECRET_KEY')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY')
    PAYSTACK_SK = os.environ.get('PAYSTACK_SEC_KEY')
    PAYSTACK_PK = os.environ.get('PAYSTACK_PUB_KEY')


class DevelopmentEnvironment(Environment):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///dev.db'


class TestingEnvironment(Environment):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///test.db'


class ProductionEnvironment(Environment):
    # SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    SQLALCHEMY_DATABASE_URI = 'sqlite:///prod.db'