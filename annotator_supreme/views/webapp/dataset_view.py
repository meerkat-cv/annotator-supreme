import flask
from flask.ext.classy import FlaskView, route, request
from annotator_supreme.views.view_tools import *
from annotator_supreme import app
from annotator_supreme.controllers.dataset_controller import DatasetController
from flask import render_template

class DatasetViewWebApp(FlaskView):
    route_base = '/'
    print('DatasetViewWebApp static')

    def __init__(self):
        self.dataset_controller = DatasetController()
        print('DatasetViewWebApp constructor')

    @route('/', methods=['GET'])
    def datasets_get(self):
        datasets = self.dataset_controller.get_datasets()
        for d in datasets:
            if len(d['annotation_labels']) > 6:
                d['annotation_labels'] = d['annotation_labels'][:6]
        return render_template('dataset.html', datasets=datasets)
