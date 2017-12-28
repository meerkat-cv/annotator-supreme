import flask
from flask.ext.classy import FlaskView, route, request
from annotator_supreme.views.view_tools import *
from annotator_supreme import app
from annotator_supreme.controllers.dataset_controller import DatasetController
from flask import render_template
from annotator_supreme.controllers.color_utils import ColorUtils
import json 

class AnnotationViewWebApp(FlaskView):
    route_base = '/'

    def __init__(self):
        self.dataset_controller = DatasetController()

    @route('/annotation', methods=['GET'])
    def annotation(self):
        # get the datasets to see which one the user wants to annotate
        datasets = self.dataset_controller.get_datasets()
        dataset_names = []
        for i,d in enumerate(datasets):
            dataset_names.append(d["name"])
            print("i", datasets[i])
            datasets[i]["category_colors"] = ColorUtils.distiguishable_colors_hex(len(d["image_categories"]))
            datasets[i]["last_modified"] = "" # it is not serialiable
            print("i", datasets[i])
            print("=========")

        print("datasets", datasets)

        # the user can choose to annotate a specif image/dataset
        sel_dataset = ""
        sel_image = ""
        if request.args.get("dataset") is not None:
            sel_dataset = request.args.get("dataset")
        if request.args.get("image") is not None:
            sel_image = request.args.get("image")


        return render_template('annotation.html', dataset_names=dataset_names, datasets=json.dumps(datasets), sel_dataset=sel_dataset, sel_image=sel_image)


    @route('/label-annotation', methods=['GET'])
    def label_annotation(self):
        # get the datasets to see which one the user wants to annotate
        datasets = self.dataset_controller.get_datasets()
        dataset_names = []
        for i,d in enumerate(datasets):
            dataset_names.append(d["name"])
            datasets[i]["category_colors"] = ColorUtils.distiguishable_colors_hex(len(d["image_categories"]))
            datasets[i]["last_modified"] = "" # it is not serialiable
            
        # the user can choose to annotate a specif dataset
        sel_dataset = ""
        if request.args.get("dataset") is not None:
            sel_dataset = request.args.get("dataset")
        app.logger.info("sel_dataset: "+sel_dataset)

        return render_template('annotation_label.html', dataset_names=dataset_names, datasets=json.dumps(datasets), sel_dataset=sel_dataset)

