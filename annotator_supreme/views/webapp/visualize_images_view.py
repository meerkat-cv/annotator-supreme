import traceback
import flask
import json
from flask.ext.classy import FlaskView, route, request
from annotator_supreme.views.view_tools import *
from annotator_supreme import app
from annotator_supreme._version import __version__
from annotator_supreme.controllers.image_controller import *
from annotator_supreme.controllers.dataset_controller import *
from annotator_supreme.controllers.color_utils import *
from flask import render_template
import json

class VisualizeImagesViewWebApp(FlaskView):
    route_base = '/'

    def __init__(self):
        self.image_controller = ImageController()
        self.dataset_controller = DatasetController()

    @route('/visualize/<dataset>', methods=['GET'])
    def image_visualize(self, dataset):
        all_imgs = self.image_controller.all_images(dataset)

        dataset_obj = self.dataset_controller.get_dataset(dataset)
        dataset_d = {
            "name": dataset_obj.dataset_name,
            "tags": dataset_obj.tags,
            "annotation_labels": dataset_obj.annotation_labels,
            "image_categories": dataset_obj.image_categories,
            "category_colors": ColorUtils.distiguishable_colors_hex(len(dataset_obj.image_categories))
        }
        return render_template('visualize_images.html', images=all_imgs, dataset=json.dumps(dataset_d))


    