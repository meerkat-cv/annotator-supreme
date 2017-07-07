import flask
from flask.ext.classy import FlaskView, route, request
from annotator_supreme.views.view_tools import *
from annotator_supreme import app
from annotator_supreme.controllers.plugins_controller import PluginsController
from annotator_supreme.controllers.dataset_controller import DatasetController
from flask import render_template

class PluginsViewWebApp(FlaskView):
    route_base = '/'

    def __init__(self):
        self.dataset_controller = DatasetController()

    @route('/plugins', methods=['GET'])
    def index(self):
        # get the datasets to see which one the user wants to annotate
        datasets = self.dataset_controller.get_datasets()
        return render_template('plugins.html', datasets=datasets)
