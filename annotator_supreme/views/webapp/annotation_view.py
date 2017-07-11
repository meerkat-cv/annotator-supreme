import flask
from flask.ext.classy import FlaskView, route, request
from annotator_supreme.views.view_tools import *
from annotator_supreme import app
from annotator_supreme.controllers.dataset_controller import DatasetController
from flask import render_template

class AnnotationViewWebApp(FlaskView):
    route_base = '/'

    def __init__(self):
        self.dataset_controller = DatasetController()

    @route('/annotation', methods=['GET'])
    def index(self):
        # get the datasets to see which one the user wants to annotate
        datasets = self.dataset_controller.get_datasets()

        # the user can choose to annotate a specif image/dataset
        sel_dataset = ""
        sel_image = ""
        if request.args.get("dataset") is not None:
            sel_dataset = request.args.get("dataset")
        if request.args.get("image") is not None:
            sel_image = request.args.get("image")


        return render_template('annotation.html', datasets=datasets, sel_dataset=sel_dataset, sel_image=sel_image)
