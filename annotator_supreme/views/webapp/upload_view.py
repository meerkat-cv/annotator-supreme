import flask
from flask.ext.classy import FlaskView, route, request
from annotator_supreme.views.view_tools import *
from annotator_supreme import app
from annotator_supreme.controllers.dataset_controller import DatasetController
from flask import render_template

class UploadViewWebApp(FlaskView):
    route_base = '/'

    def __init__(self):
        self.dataset_controller = DatasetController()

    @route('/add/images', methods=['GET'])
    def datasets(self):
        datasets = self.dataset_controller.get_datasets()
        return render_template('upload_images.html', datasets=datasets)

    @route('/upload_images', methods=['POST'])
    def upload_images(self):
        return 200, ''
