from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Load the confguration
app.config.from_object('config')

db = SQLAlchemy(app)

from app import server, models
from flasgger import Swagger

# Configurue Swagger
app.config['SWAGGER'] = {
    "swagger_version": "2.0",
    "specs": [
        {
            "version": "1.0.0",
            "title": "Inventory",
            "description": "This is an Inventory server.",
            "endpoint": 'v1_spec',
            "route": '/v1/spec'
        }
    ]
}
Swagger(app)