from flask import jsonify
from app.server import app
from app.models import DataValidationError
from flask_api import status

BAD_REQUEST_ERROR = 'Bad Request.'
METHOD_NOT_ALLOWED_ERROR = 'Method Not Allowed'
NOT_FOUND_ERROR = 'Not Found.'
UNSUPPORTED_MEDIA_TYPE_ERROR = 'Unsupported media type'
INTERNAL_SERVER_ERROR = 'Internal Server Error'

######################################################################
# Error Handlers
######################################################################
@app.errorhandler(DataValidationError)
def request_validation_error(error):
    """ Handles all data validation issues from the model """
    app.logger.error(error.message)
    return jsonify(status=status.HTTP_400_BAD_REQUEST, error=BAD_REQUEST_ERROR,
                   message=error.message), status.HTTP_400_BAD_REQUEST

@app.errorhandler(status.HTTP_400_BAD_REQUEST)
def bad_request(error):
    """ Handles requests that have bad or malformed data """
    app.logger.error(str(error))
    return jsonify(status=status.HTTP_400_BAD_REQUEST, error=BAD_REQUEST_ERROR,
                   message=error.description), status.HTTP_400_BAD_REQUEST

@app.errorhandler(status.HTTP_404_NOT_FOUND)
def not_found(error):
    """ Handles product information that cannot be found """
    message = error.message or str(error)
    app.logger.error(message)
    return jsonify(status=status.HTTP_404_NOT_FOUND, error=NOT_FOUND_ERROR,
                   message=error.message), status.HTTP_404_NOT_FOUND

@app.errorhandler(status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)
def mediatype_not_supported(error):
    """ Handles unsuppoted media requests with 415_UNSUPPORTED_MEDIA_TYPE """
    message = error.message or str(error)
    app.logger.error(message)
    return jsonify(status=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, error=UNSUPPORTED_MEDIA_TYPE_ERROR,
    			   message=message), status.HTTP_415_UNSUPPORTED_MEDIA_TYPE

@app.errorhandler(status.HTTP_500_INTERNAL_SERVER_ERROR)
def internal_server_error(error):
    """ Handles unexpected server error with 500_SERVER_ERROR """
    message = error.message or str(error)
    app.logger.error(message)
    return jsonify(status=status.HTTP_500_INTERNAL_SERVER_ERROR, error=INTERNAL_SERVER_ERROR,
    			   message=message), status.HTTP_500_INTERNAL_SERVER_ERROR
