import flask
from flask.ext.classy import FlaskView, route, request
from annotator_supreme.models.bbox_model import BBox
from annotator_supreme.controllers.image_controller import ImageController
from annotator_supreme.controllers.image_utils import ImageUtils
from annotator_supreme.views import view_tools
from annotator_supreme.views import error_views
import cv2

class ImageEditView(FlaskView):
    route_base = '/'

    def __init__(self):
        self.controller = ImageController()

    @route('/image/edit/rotate/<dataset>/<imageid>', methods=['GET'])
    def rotate_image(self, dataset, imageid):
        (ok, error, orientation) = view_tools.get_param_from_request(request, "orientation")
        if not ok or orientation == "":
            raise error_views.InvalidParametersError("Need to specify the orientation for the rotation: cw or ccw")

        (ok, error) = self.controller.rotate_image(dataset, imageid, orientation)
        if not ok:
            raise error_views.InvalidParametersError(error)

        return "", 200


    @route('/image/edit/flip/<dataset>/<imageid>', methods=['GET'])
    def flip_image(self, dataset, imageid):
        (ok, error, direction) = view_tools.get_param_from_request(request, "direction")
        if not ok or direction == "":
            raise error_views.InvalidParametersError("Need to specify the direction for the rotation: h or v")

        (ok, error) = self.controller.flip_image(dataset, imageid, direction)
        if not ok:
            raise error_views.InvalidParametersError(error)

        return "", 200


    @route('/image/edit/ratio/<dataset>/<imageid>', methods=['GET'])
    def ratio_image(self, dataset, imageid):
        (ok, error, aspect) = view_tools.get_param_from_request(request, "aspect_ratio")
        if not ok or aspect == "":
            raise error_views.InvalidParametersError("Need to specify the aspect ratio: 4:3")

        (ok, error) = self.controller.set_aspect_ratio_image(dataset, imageid, aspect)
        if not ok:
            raise error_views.InvalidParametersError(error)

        return "", 200


        