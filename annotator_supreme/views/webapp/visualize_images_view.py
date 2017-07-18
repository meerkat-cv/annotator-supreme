import traceback
import flask
import json
from flask.ext.classy import FlaskView, route, request
from annotator_supreme.views.view_tools import *
from annotator_supreme import app
from annotator_supreme._version import __version__
from annotator_supreme.controllers.image_controller import *
from flask import render_template

class VisualizeImagesViewWebApp(FlaskView):
    route_base = '/'

    def __init__(self):
        self.image_controller = ImageController()

    @route('/visualize/<dataset>', methods=['GET'])
    def image_visualize(self, dataset):
        all_imgs = self.image_controller.all_images(dataset)
        return render_template('visualize_images.html', images=all_imgs, dataset=dataset)


    