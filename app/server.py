"""
Inverntory Management System Service
"""

from __future__ import print_function
import logging
import sys
from app import app
from app.models import DataValidationError, ProductInformation
from flask import abort, jsonify, make_response, request, url_for
from flask_api import status
from werkzeug.exceptions import BadRequest, NotFound

######################################################################
#  Fixed Global Variables
######################################################################
# HTTP request methods
DELETE = 'DELETE'
GET = 'GET'
POST = 'POST'
PUT = 'PUT'
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
INVALID_PARAMETER_MSG = 'Your request contains invalid parameters. ' \
        'Please check your request and try again.'
# Content type
CONTENT_TYPE = 'Content-Type'
JSON = 'application/json'
# Locations
GET_PROD_INFO = 'get_prod_info'
LOCATION = 'Location'


######################################################################
# Error Handlers
######################################################################
@app.errorhandler(DataValidationError)
def request_validation_error(error):
    """ Handles all data validation issues from the model """
    app.logger.info(error.message)
    return jsonify(status=status.HTTP_400_BAD_REQUEST, error=BAD_REQUEST_ERROR,
                   message=error.message), status.HTTP_400_BAD_REQUEST

@app.errorhandler(status.HTTP_400_BAD_REQUEST)
def bad_request(error):
    """ Handles requests that have bad or malformed data """
    app.logger.info(str(error))
    return jsonify(status=status.HTTP_400_BAD_REQUEST, error=BAD_REQUEST_ERROR,
                   message=error.description), status.HTTP_400_BAD_REQUEST

@app.errorhandler(status.HTTP_404_NOT_FOUND)
def not_found(error):
    """ Handles product information that cannot be found """
    message = error.message or str(error)
    app.logger.info(message)
    return jsonify(status=status.HTTP_404_NOT_FOUND, error=NOT_FOUND_ERROR,
                   message=error.message), status.HTTP_404_NOT_FOUND

######################################################################
# API placeholder
######################################################################
@app.route('/')
def index():
    """ Return help information about the API """
    return jsonify(
        name='Inventory Management REST API Service',
        version='1.0',
        docs=request.base_url + 'apidocs/index.html',
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

@app.route('/inventory', methods=[GET])
def query_prod_info():
    """ Query specific entries in the Inventory system """
    all_prod_info = []
    if request.args.get('prod_name'):
        prod_name = request.args.get('prod_name')
        all_prod_info = ProductInformation.find_by_name(prod_name)
    elif request.args.get('quantity'):
        quantity = request.args.get('quantity')
        try:
            quantity = int(quantity)
            all_prod_info = ProductInformation.find_by_quantity(quantity)
        except ValueError:
            abort(status.HTTP_400_BAD_REQUEST, INVALID_PARAMETER_MSG)
    elif request.args.get('condition'):
        condition = request.args.get('condition')
        if condition in ['new', 'used', 'open-boxed']:
            all_prod_info = ProductInformation.find_by_condition(condition)
        else:
            abort(status.HTTP_400_BAD_REQUEST, INVALID_PARAMETER_MSG)
    elif not request.args:
        all_prod_info = ProductInformation.list_all()
    else:
        abort(status.HTTP_400_BAD_REQUEST, INVALID_PARAMETER_MSG)

    results = [prod_info.serialize() for prod_info in all_prod_info]
    return jsonify(results), status.HTTP_200_OK

@app.route('/inventory/<int:prod_id>', methods=[GET])
def get_prod_info(prod_id):
    """ Return ProductInformation identified by prod_id """
    prod_info = ProductInformation.find(prod_id)
    if not prod_info:
        raise NotFound(NOT_FOUND_MSG.format(prod_id))
    return jsonify(prod_info.serialize()), status.HTTP_200_OK

@app.route('/inventory', methods=[POST])
def create_prod_info():
    """
    Creates a ProductInformation
    This endpoint will create a ProductInformation based the data in the body that is posted
    ---
    tags:
        -   Inventory
    consumes:
        -   application/json
    produces:
        -   application/json
    definitions:
        Product:
            type: object
            properties:
                prod_id:
                    type: integer
                    description: Unique ID of the product.
                prod_name:
                    type: string
                    description: Name for the product.
                new_qty:
                    type: integer
                    description: Quantity of condition "new".
                used_qty:
                    type: integer
                    description: Quantity of condition "used".
                open_boxed_qty:
                    type: integer
                    description: Quantity of condition "open boxed".
                restock_level:
                    type: integer
                    minimum: -1
                    description: Bottom line of a product's quantity with condition "new".
                restock_amt:
                    type: integer
                    description: Quantity to be added to a product's quantity with condition "new".
    parameters:
        -   in: body
            name: body
            required: true
            description: 
            schema:
                id: data
                required:
                    - prod_id
                    - prod_name
                $ref: '#/definitions/Product'
                
    responses:
        201:
            description: Product information created
            schema:
                $red: '#/definitions/Product'
        400:
            description: Bad Request (invalid posted data)        
    """
    check_content_type(JSON)
    prod_info = ProductInformation()
    prod_info.deserialize(request.get_json())

    if ProductInformation.find(prod_info.prod_id):
        raise BadRequest(CANNOT_CREATE_MSG.format(prod_info.prod_id))

    prod_info.save()
    message = prod_info.serialize()
    location_url = url_for(GET_PROD_INFO, prod_id=prod_info.prod_id, _external=True)
    return make_response(jsonify(message), status.HTTP_201_CREATED,
                         {
                             LOCATION: location_url
                         })

@app.route('/inventory/<int:prod_id>', methods=[DELETE])
def delete_prod_info(prod_id):
    """
    Deletes a ProductInformation
    This endpoint will delete a ProductInformation based on the prod_id specified in the path.
    Should always return 200OK.
    """
    prod_info = ProductInformation.find(prod_id)
    if prod_info:
        prod_info.delete()
    return make_response('', status.HTTP_200_OK)

@app.route('/inventory/<int:prod_id>', methods=[PUT])
def update_prod_info(prod_id):
    """
    Update prodcut information

    This endpoint will update a ProductInformation based on data that id posted in the body
    """
    check_content_type(JSON)
    prod_info = ProductInformation.find(prod_id)
    if not prod_info:
        raise NotFound(NOT_FOUND_MSG.format(prod_id))

    prod_info.deserialize_update(request.get_json())
    prod_info.save()
    return make_response(jsonify(prod_info.serialize()), status.HTTP_200_OK)


######################################################################
# Action placeholder
######################################################################
@app.route('/inventory/<int:prod_id>/restock', methods=[PUT])
def restock_action(prod_id):
    """
    Restock new quantity.

    This endpoint will update the number of new_qty of the given prod_id.
    """
    check_content_type(JSON)
    prod_info = ProductInformation.find(prod_id)
    if not prod_info:
        raise NotFound(NOT_FOUND_MSG.format(prod_id))

    data = request.get_json()
    add_amt = data.get('restock_amt')
    if (len(list(data.keys())) != 1) or (add_amt is None) or (add_amt < 0):
        raise BadRequest("Please only give 'restock_amt' as input.")

    prod_info.restock(add_amt)
    prod_info.save()
    return make_response(jsonify(prod_info.serialize()), status.HTTP_200_OK)

######################################################################
#  U T I L I T Y   F U N C T I O N S
######################################################################
def init_db():
    """ Initialies the SQLAlchemy app """
    ProductInformation.init_db()

def check_content_type(content_type):
    """ Checks that the media type is correct """
    if request.headers[CONTENT_TYPE] == content_type:
        return
    app.logger.error(INVALID_CONTENT_TYPE_ERROR, request.headers[CONTENT_TYPE])
    abort(status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, INVALID_CONTENT_TYPE_MSG.format(content_type))

def initialize_logging(log_level=logging.INFO):
    """ Initialized the default logging to STDOUT """
    if not app.debug:
        print("Setting up logging...")
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
