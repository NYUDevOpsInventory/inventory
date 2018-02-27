"""
Inverntory Management System Service

Paths:
------
GET /
- Returns useful information about the service.

GET /inventory
- Returns all the product information in the Inventory.

GET /inventory/{prod_id}
- Returns production information about a certain product.

POST /inventory
- Adds a new product with its information to the inventory.

PUT /inventory/{prod_id}
- Updates information of a product.

DELETE /inventory/{prod_id}
- Deletes product information with the given product id.

GET /inventory?{prod_name|quantity|condition=val}
- Returns all products' information meeting given requirement.

PUT /inventory/{prod_id}/restock
- An action triggers restocking for a product.
"""

from flask import Flask, jsonify, url_for, make_response, request
from flask_api import status
from models import DataValidationError, ProductInformation
from werkzeug.exceptions import BadRequest, NotFound
import os

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
# Error messages
CANNOT_CREATE_ERROR = "Product with id '{}' already existed. Cannot create new product \
        information with the same prod_id."
# Content type
JSON = 'application/json'

# Create Flask application
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URL'] = 'sqlite:////tmp/test.db'

######################################################################
# Error Handlers
######################################################################
@app.errorhandler(DataValidationError)
def request_validation_error(error):
    """ Handles all data validation issues from the model """
    return bad_request(error)

@app.errorhandler(400)
def bad_request(error):
    """ Handles requests that have bad or malformed data """
    return jsonify(status=400, error='Bad Request', message=error.message), 400

@app.errorhandler(404)
def not_found(error):
    """ Handles product information that cannot be found """
    return jsonify(status=404, error='Not Found', message=error.message), 404

@app.errorhandler(405)
def method_not_supported(error):
    """ Handles bad method calls """
    return jsonify(status=405, error='Method not Allowed',
                   message='Your request method is not supported.' \
                   ' Check your HTTP method and try again.'), 405

@app.errorhandler(500)
def internal_server_error(error):
    """ Handles catostrophic errors """
    return jsonify(status=500, error='Internal Server Error', message=error.message), 500

######################################################################
# API placeholder
######################################################################
@app.route(PATH_ROOT)
def index():
    """ Return something useful by default """
    return jsonify(name='Inventory Root'), status.HTTP_200_OK

@app.route(PATH_INVENTORY, methods=[GET])
def list_inventory():
    """ Return all entries in the Inventory system """
    results = [prod_info.serialize() for prod_info in ProductInformation.list_all()]
    return jsonify(results), status.HTTP_200_OK

@app.route(PATH_INVENTORY_PROD_ID, methods=[GET])
def get_prod_info(prod_id):
    """ Return ProductInformation identified by prod_id """
    prod_info = ProductInformation.find(prod_id)
    if not prod_info:
        raise NotFound("Product with id '{}' was not found in Inventory".format(prod_id))
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

    if (prod_info.find(prod_info.prod_id)):
        raise BadRequest(CANNOT_CREATE_ERROR.format(prod_info.prod_id))

    prod_info.save()
    message = prod_info.serialize()
    location_url = url_for('get_prod_info', prod_id=prod_info.prod_id, _external=True)
    return make_response(jsonify(message), status.HTTP_201_CREATED,
            {
                'Location': location_url
            })

######################################################################
#  U T I L I T Y   F U N C T I O N S
######################################################################
def init_db():
    """ Initialies the SQLAlchemy app """
    global app
    ProductInformation.init_db(app)

def check_content_type(content_type):
    """ Checks that the media type is correct """
    if request.headers['Content-Type'] == content_type:
        return
    app.logger.error('Invalid Content-Type: %s', request.headers['Content-Type'])
    abort(415, 'Content-Type must be {}'.format(content_type))

######################################################################
#   M A I N
######################################################################
if __name__ == "__main__":
    print("**********************************")
    print("   INVENTORY MANAGEMENT SERVICE   ")
    print("**********************************")
    init_db()  # make our sqlalchemy tables
    app.run(host='0.0.0.0', port=int(PORT), debug=DEBUG)
