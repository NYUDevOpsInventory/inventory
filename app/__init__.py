from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import logging

app = Flask(__name__)

# Initialize MariaDB connection
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:123@localhost:3306/inventory'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['LOGGING_LEVEL'] = logging.INFO

db = SQLAlchemy(app)

from app import server, models