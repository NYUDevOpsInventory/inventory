import logging
from app.vcap_services import get_database_uri

SQLALCHEMY_DATABASE_URI = get_database_uri()
SQLALCHEMY_TRACK_MODIFICATIONS = False
LOGGING_LEVEL = logging.INFO
