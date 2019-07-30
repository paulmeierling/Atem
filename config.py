import os 

class Config(object):
    #DATABASE CONFIG
    SECRET_KEY = 'you-will-never-guess'
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://atem:X8iaFBvTckcpVb3@atem.cazulltrpt4a.us-east-2.rds.amazonaws.com:3306/atem'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    #ENV CONFIG
    FLASK_ENV = 'development'
    DEBUG = True
    TESTING = True
    APP_ROOT = os.path.dirname(os.path.abspath(__file__))  
    
    #S3 CONFIG
    S3_BUCKET                 = "elasticbeanstalk-us-east-1-632719977842"
    S3_KEY                    = "AKIAZGUIMVVZMNM3OCGL"
    S3_SECRET                 = "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"
    S3_LOCATION               = 'http://{}.s3.amazonaws.com/'.format(S3_BUCKET)

