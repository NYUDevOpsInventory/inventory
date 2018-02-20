"""
Inverntory Management System Server
"""

import os
# import sys
# import logging
from flask import Flask, jsonify
# from flask import Response, request, json, url_for, make_response
from models import DataValidationError

# Pull options from environment
DEBUG = (os.getenv('DEBUG', 'False') == 'True')
PORT = os.getenv('PORT', '5000')

# Create Flask application
app = Flask(__name__)

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
    return jsonify(message='List all inventory API'), HTTP_200_OK

@app.route('/inventory/<int:entry_id>', methods=['GET'])
def get_entry(entry_id):
    """ Return entry identified by entry_id """
    message = {'message' : 'GET request for entry %s' % str(entry_id)}
    return jsonify(message), HTTP_200_OK

######################################################################
#   M A I N
######################################################################
if __name__ == "__main__":
    print("**********************************")
    print("   INVENTORY MANAGEMENT SERVICE   ")
    print("**********************************")
    app.run(host='0.0.0.0', port=int(PORT), debug=DEBUG)
