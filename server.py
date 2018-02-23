"""
Inverntory Management System Server
"""

import os
# import sys
# import logging
from flask import Flask, jsonify, url_for, make_response, request
# from flask_sqlalchemy import SQLAlchemy
# from flask import Response, json
from models import DataValidationError, Entry
from werkzeug.exceptions import NotFound

# Pull options from environment
DEBUG = (os.getenv('DEBUG', 'False') == 'True')
PORT = os.getenv('PORT', '5000')

# Create Flask application
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URL'] = 'sqlite:////tmp/test.db'

# Status Codes
HTTP_200_OK = 200
HTTP_201_CREATED = 201
HTTP_204_NO_CONTENT = 204
HTTP_400_BAD_REQUEST = 400
HTTP_404_NOT_FOUND = 404
HTTP_409_CONFLICT = 409

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
    """ Handles Pets that cannot be found """
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
@app.route('/')
def index():
    """ Return something useful by default """
    return jsonify(name='Inventory Root'), HTTP_200_OK

@app.route('/inventory', methods=['GET'])
def list_inventory():
    """ Return all entries in the Inventory system """
    results = [entry.serialize() for entry in Entry.list_all()]
    return jsonify(results), HTTP_200_OK

@app.route('/inventory/<int:prod_id>', methods=['GET'])
def get_entry(prod_id):
    """ Return entry identified by prod_id """
    entry = Entry.find(prod_id)
    if not entry:
        raise NotFound("Product with id '{}' was not found in Inventory".format(prod_id))
    return jsonify(entry.serialize()), HTTP_200_OK

@app.route('/inventory', methods=['POST'])
def create_entry():
    """
    Creates an Inventory entry
    This endpoint will create an entry based the data in the body that is posted
    """
    check_content_type('application/json')
    entry = Entry()
    entry.deserialize(request.get_json())
    entry.save()
    message = entry.serialize()
    location_url = url_for('get_entry', prod_id=entry.prod_id, _external=True)
    return make_response(jsonify(message), HTTP_201_CREATED,
                         {
                             'Location': location_url
                         })

######################################################################
#  U T I L I T Y   F U N C T I O N S
######################################################################

def init_db():
    """ Initialies the SQLAlchemy app """
    global app
    Entry.init_db(app)

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
