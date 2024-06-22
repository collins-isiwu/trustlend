import os

class Environment:
    SECRET_KEY = os.environ.get('SECRET_KEY')
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class DevelopmentEnvironment(Environment):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///dev.db'


class TestingEnvironment(Environment):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///test.db'