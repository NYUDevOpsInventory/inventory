import logging
from app.vcap_services import get_database_uri

LOGGING_LEVEL = logging.INFO
SQLALCHEMY_DATABASE_URI = get_database_uri()
SQLALCHEMY_TRACK_MODIFICATIONS = False
SWAGGER = {
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
