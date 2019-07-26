import os 

class Config(object):
    SECRET_KEY = 'you-will-never-guess'
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://atem:X8iaFBvTckcpVb3@atem.cazulltrpt4a.us-east-2.rds.amazonaws.com:3306/atem'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    FLASK_ENV = 'development'
    DEBUG = True
    TESTING = True
    APP_ROOT = os.path.dirname(os.path.abspath(__file__))  

