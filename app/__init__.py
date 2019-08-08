from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import boto3, botocore

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
s3 = boto3.client("s3", aws_access_key_id=Config.S3_KEY, aws_secret_access_key=Config.S3_SECRET)

from app import routes, models