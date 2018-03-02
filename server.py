"""
Inverntory Management System Service
"""

from flask import Flask, jsonify, url_for, make_response, request
from flask_api import status
from models import DataValidationError, ProductInformation
from werkzeug.exceptions import BadRequest, NotFound
import os
import logging
import sys

######################################################################
#  Fixed Global Variables
######################################################################
# Pull options from environment
DEBUG = (os.getenv('DEBUG', 'False') == 'True')
PORT = os.getenv('PORT', '5000')
# HTTP request methods
DELETE = 'DELETE'
GET = 'GET'
POST = 'POST'
PUT = 'PUT'
# API paths
PATH_ROOT = '/'
PATH_INVENTORY = '/inventory'
PATH_INVENTORY_PROD_ID = '/inventory/<int:prod_id>'
# Errors
BAD_REQUEST_ERROR = 'Bad Request.'
INTERNAL_SERVER_ERROR = 'Internal Server Error'
INVALID_CONTENT_TYPE_ERROR = 'Invalid Content-Type: %s'
METHOD_NOT_ALLOWED_ERROR = 'Method Not Allowed'
NOT_FOUND_ERROR = 'Not Found.'
# Messages
CANNOT_CREATE_MSG = "Product with id '{}' already existed. Cannot create new product " \
        "information with the same prod_id."
INVALID_CONTENT_TYPE_MSG = 'Content-Type must be {}'
METHOD_NOT_ALLOWED_MSG = 'Your request method is not supported.' \
                   ' Check your HTTP method and try again.'
NOT_FOUND_MSG = "Product with id '{}' was not found in Inventory"
# Content type
CONTENT_TYPE = 'Content-Type'
JSON = 'application/json'
# Locations
GET_PROD_INFO = 'get_prod_info'
LOCATION = 'Location'

# Create Flask application
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URL'] = 'sqlite:////tmp/test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['LOGGING_LEVEL'] = logging.INFO

######################################################################
# Error Handlers
######################################################################
@app.errorhandler(DataValidationError)
def request_validation_error(error):
    """ Handles all data validation issues from the model """
    return bad_request(error)

@app.errorhandler(status.HTTP_400_BAD_REQUEST)
def bad_request(error):
    """ Handles requests that have bad or malformed data """
    message = error.message or str(error)
    app.logger.info(message)
    return jsonify(status = status.HTTP_400_BAD_REQUEST, error = BAD_REQUEST_ERROR,
            message = error.message), status.HTTP_400_BAD_REQUEST

@app.errorhandler(status.HTTP_404_NOT_FOUND)
def not_found(error):
    """ Handles product information that cannot be found """
    message = error.message or str(error)
    app.logger.info(message)
    return jsonify(status = status.HTTP_404_NOT_FOUND, error = NOT_FOUND_ERROR,
            message = error.message), status.HTTP_404_NOT_FOUND

@app.errorhandler(status.HTTP_405_METHOD_NOT_ALLOWED)
def method_not_supported(error):
    """ Handles bad method calls """
    message = error.message or str(error)
    app.logger.info(message)
    return jsonify(status = status.HTTP_405_METHOD_NOT_ALLOWED, error = METHOD_NOT_ALLOWED_ERROR,
                   message = METHOD_NOT_ALLOWED_MSG), status.HTTP_405_METHOD_NOT_ALLOWED

@app.errorhandler(status.HTTP_500_INTERNAL_SERVER_ERROR)
def internal_server_error(error):
    """ Handles catostrophic errors """
    message = error.message or str(error)
    app.logger.info(message)
    return jsonify(status = status.HTTP_500_INTERNAL_SERVER_ERROR, error = INTERNAL_SERVER_ERROR,
            message = error.message), status.HTTP_500_INTERNAL_SERVER_ERROR

######################################################################
# API placeholder
######################################################################
@app.route(PATH_ROOT)
def index():
    """ Return help information about the API """
    return jsonify(
        name='Inventory Management REST API Service',
        version='1.0',
        usage={
            'help': 'GET /',
            'list all': 'GET /inventory',
            'read': 'GET /inventory/{prod_id}',
            'create': 'POST /inventory',
            'update': 'PUT /inventory/{prod_id}',
            'delete': 'DELETE /inventory/{prod_id}',
            'query': 'GET /inventory?{prod_name|quantity|condition=val}',
            'restock': 'PUT /inventory/{prod_id}/restock',
        },
    ), status.HTTP_200_OK

@app.route(PATH_INVENTORY, methods=[GET])
def list_all_prod_info():
    """ Return all entries in the Inventory system """
    results = [prod_info.serialize() for prod_info in ProductInformation.list_all()]
    return jsonify(results), status.HTTP_200_OK

@app.route(PATH_INVENTORY_PROD_ID, methods=[GET])
def get_prod_info(prod_id):
    """ Return ProductInformation identified by prod_id """
    prod_info = ProductInformation.find(prod_id)
    if not prod_info:
        raise NotFound(NOT_FOUND_MSG.format(prod_id))
    return jsonify(prod_info.serialize()), status.HTTP_200_OK

@app.route(PATH_INVENTORY, methods=[POST])
def create_prod_info():
    """
    Creates a ProductInformation
    This endpoint will create a ProductInformation based the data in the body that is posted
    """
    check_content_type(JSON)
    prod_info = ProductInformation()
    prod_info.deserialize(request.get_json())

    if (ProductInformation.find(prod_info.prod_id)):
        raise BadRequest(CANNOT_CREATE_MSG.format(prod_info.prod_id))

    prod_info.save()
    message = prod_info.serialize()
    location_url = url_for(GET_PROD_INFO, prod_id=prod_info.prod_id, _external=True)
    return make_response(jsonify(message), status.HTTP_201_CREATED,
            {
                LOCATION: location_url
            })

@app.route(PATH_INVENTORY_PROD_ID, methods=[DELETE])
def delete_prod_info(prod_id):
    """
    Deletes a ProductInformation
    This endpoint will delete a ProductInformation based on the prod_id specified in the path.
    Should always return 200OK.
    """
    prod_info = ProductInformation.find(prod_id)
    if prod_info:
        prod_info.delete()
    return make_response('Product information deleted.', status.HTTP_200_OK)

######################################################################
#  U T I L I T Y   F U N C T I O N S
######################################################################
def init_db():
    """ Initialies the SQLAlchemy app """
    global app
    ProductInformation.init_db(app)

def check_content_type(content_type):
    """ Checks that the media type is correct """
    if request.headers[CONTENT_TYPE] == content_type:
        return
    app.logger.error(INVALID_CONTENT_TYPE_ERROR, request.headers[CONTENT_TYPE])
    abort(status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, INVALID_CONTENT_TYPE_MSG.format(content_type))

def initialize_logging(log_level=logging.INFO):
    """ Initialized the default logging to STDOUT """
    if not app.debug:
        print ("Setting up logging...")
        # Set up default logging for submodules to use STDOUT
        # datefmt='%m/%d/%Y %I:%M:%S %p'
        fmt = '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
        logging.basicConfig(stream=sys.stdout, level=log_level, format=fmt)
        # Make a new log handler that uses STDOUT
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(logging.Formatter(fmt))
        handler.setLevel(log_level)
        # Remove the Flask default handlers and use our own
        handler_list = list(app.logger.handlers)
        for log_handler in handler_list:
            app.logger.removeHandler(log_handler)
        app.logger.addHandler(handler)
        app.logger.setLevel(log_level)
        app.logger.info('Logging handler established')

######################################################################
#   M A I N
######################################################################
if __name__ == "__main__":
    print("**********************************")
    print("   INVENTORY MANAGEMENT SERVICE   ")
    print("**********************************")
    initialize_logging(logging.INFO)
    init_db()  # make our sqlalchemy tables
    app.run(host='0.0.0.0', port=int(PORT), debug=DEBUG)
