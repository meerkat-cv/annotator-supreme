import datetime
import flask

from annotator_supreme import app



@app.errorhandler(401)
def unauthorized(e):
    res_obj = {'error': 'Unauthorized access',
                'message': 'Field api_key not present in request headers or not valid'
    }
    return flask.jsonify(res_obj), 401

@app.errorhandler(415)
def unauthorized(e):
    res_obj = {'error': 'Unsupported Media Type',
                'message': 'Invalid or empty content-type in headers'
    }
    return flask.jsonify(res_obj), 415


## 500 - Internal Error
class InternalError(Exception):
    status_code = 500

    def __init__(self, message):
        Exception.__init__(self)
        self.message = message
        
    def to_dict(self):
        res_obj = {'error': 'Internal Error',
                'message': self.message
        }
        return res_obj


@app.errorhandler(InternalError)
def handle_internal_error(error):
    response = flask.jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


## 432 - Invalid parameters
class InvalidParametersError(Exception):
    status_code = 432

    def __init__(self, message):
        Exception.__init__(self)
        self.message = message
        
    def to_dict(self):
        res_obj = {'error': 'Invalid parameters',
                'message': self.message
        }
        app.logger.warning('432 message:'+self.message)
        return res_obj


@app.errorhandler(InvalidParametersError)
def handle_invalid_parameters(error):
    response = flask.jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


## 403 - QuotaExceded
class QuotaExceeded(Exception):
    status_code = 403

    def __init__(self, subscription_date):
        Exception.__init__(self)
        self.day_of_month = datetime.datetime.fromtimestamp(subscription_date).strftime('%d')
        
    def to_dict(self):
        res_obj = {'error': 'Quota limits exceeded',
                'message': 'You reach the monthly limit of your subscription plan. The cycle will end on day '+self.day_of_month+'.'
        }
        return res_obj


@app.errorhandler(QuotaExceeded)
def handle_quota_error(error):
    response = flask.jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


