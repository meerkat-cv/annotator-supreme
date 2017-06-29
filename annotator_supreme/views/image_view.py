import flask
from flask.ext.classy import FlaskView, route, request
from annotator_supreme.controllers.image_controller import ImageController
from annotator_supreme.views import view_tools
from annotator_supreme.views import error_views

class ImageView(FlaskView):
    route_base = '/'

    def __init__(self):
        self.controller = ImageController()

    @route('/image/<dataset>/all', methods=['GET'])
    def get_all_images(self, dataset):
        obj = self.controller.all_images(dataset)
        return flask.jsonify({"images": obj})

    @route('/image/<dataset>/add', methods=['POST'])
    def create_image(self, dataset):
        (ok, error, image) = view_tools.get_image_from_request(request)
        if not ok:
            raise error_views.InvalidParametersError(error)

        (ok, error, image_id) = self.controller.create_image(dataset, image)
        if not ok:
            raise error_views.InvalidParametersError(error)

        image_url = "{}/{}".format(dataset, image_id)
        return flask.jsonify({"imageId": image_id,
                                "imageUrl": image_url})
