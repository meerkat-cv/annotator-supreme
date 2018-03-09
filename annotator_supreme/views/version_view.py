import flask
import os
import logging
from flask.ext.classy import FlaskView, route, request
from annotator_supreme._version import __version__

class VersionView(FlaskView):
    route_base = '/'

    def __init__(self):
        self.current_version = __version__
        self.source_commit = os.getenv("SOURCE_COMMIT")
        
        self.logger = logging.getLogger('annotator_supreme.version')
        self.logger.info('Version : %s ; Source commit : %s', self.current_version, self.source_commit)
        
        pass

    @route('/version', methods=['GET'])
    def version(self):
        obj = {"version": self.current_version, "source_commit": self.source_commit}

        return flask.jsonify(obj)

    
