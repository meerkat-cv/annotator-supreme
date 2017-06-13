import flask
from flask.ext.classy import FlaskView, route, request
from annotator_supreme.controllers.dataset_controller import DatasetController
from annotator_supreme.views import view_tools
from annotator_supreme.views import error_views

class DatasetView(FlaskView):
    route_base = '/'

    def __init__(self):
        self.controller = DatasetController()

    @route('/dataset/all', methods=['GET'])
    def get_all_datasets(self):
        obj = self.controller.get_datasets()
        return flask.jsonify({"datasets": obj})

    @route('/dataset/create', methods=['POST'])
    def create_datasets(self):
        (ok, error, name) = view_tools.get_param_from_request(request, "name")
        if not ok:
            raise error_views.InvalidParametersError(error)

        (ok, error, tags) = view_tools.get_param_from_request(request, "tags")
        if not ok:
            raise error_views.InvalidParametersError(error)

        self.controller.create_dataset(name, tags)
        return flask.jsonify({"ok": "to-do"})