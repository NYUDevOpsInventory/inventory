import logging
from app.vcap_services import get_database_uri
from app import app
from flasgger import Swagger

SQLALCHEMY_DATABASE_URI = get_database_uri()
SQLALCHEMY_TRACK_MODIFICATIONS = False
LOGGING_LEVEL = logging.INFO

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