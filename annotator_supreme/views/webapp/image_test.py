import flask
from flask.ext.classy import FlaskView, route, request
from annotator_supreme.views.view_tools import *
from annotator_supreme import app
from annotator_supreme._version import __version__
from flask import render_template

class ImageTestViewWebApp(FlaskView):
    route_base = '/'

    def __init__(self):
        pass

    @route('/image_test', methods=['GET'])
    def index(self):
        return render_template('image_test.html', version=__version__)
