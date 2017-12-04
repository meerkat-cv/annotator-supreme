import flask
import os
from flask.ext.classy import FlaskView, route, request
from annotator_supreme._version import __version__

class VersionView(FlaskView):
    route_base = '/'

    def __init__(self):
        pass

    @route('/version', methods=['GET'])
    def version(self):
        current_version = __version__
        source_commit = os.getenv("SOURCE_COMMIT")
        obj = {"version": current_version, "source_commit": source_commit}

        return flask.jsonify(obj)
