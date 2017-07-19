import flask
from flask.ext.classy import FlaskView, route, request
from annotator_supreme.models.bbox_model import BBox
from annotator_supreme.controllers.image_controller import ImageController
from annotator_supreme.controllers.image_utils import ImageUtils
from annotator_supreme.views import view_tools
from annotator_supreme.views import error_views
import cv2

class ImageView(FlaskView):
    route_base = '/'

    def __init__(self):
        self.controller = ImageController()

    @route('/image/<dataset>/<imageid>', methods=['DELETE'])
    def delete_image(self, dataset, imageid):
        (ok, error) = self.controller.delete_image(dataset, imageid)
        if not ok:
            raise error_views.InvalidParametersError(error)
        else:
            return '', 200


    @route('/image/details/<dataset>/<imageid>', methods=['GET'])
    def get_image_details(self, dataset, imageid):
        img_details = self.controller.get_image_details(dataset, imageid)
        
        return flask.jsonify({"image": img_details})

    @route('/image/<dataset>/<imageid>', methods=['GET'])
    def get_image(self, dataset, imageid):
        img = self.controller.get_image(dataset, imageid)
        fileid = "img" # uuid.uuid4().hex
        full_filename = 'annotator_supreme/static/'+fileid+'.jpg'
        cv2.imwrite(full_filename, img)
        filename = 'static/'+fileid+'.jpg'

        return flask.send_file(filename, mimetype='image/jpeg')


    @route('/image/thumb/<dataset>/<imageid>', methods=['GET'])
    def get_image_thumb(self, dataset, imageid):
        img = self.controller.get_image(dataset, imageid)
        anno = self.controller.get_image_anno(dataset, imageid)
        thumb = ImageUtils.create_thumbnail(img, anno)
        fileid = "imgthumb" # uuid.uuid4().hex
        full_filename = 'annotator_supreme/static/'+fileid+'.jpg'
        cv2.imwrite(full_filename, thumb)
        filename = 'static/'+fileid+'.jpg'

        return flask.send_file(filename, mimetype='image/jpeg')


    @route('/image/<dataset>/all', methods=['GET'])
    def get_all_images(self, dataset):

        obj = ImageController.all_images(dataset)
        return flask.jsonify({"images": obj})

    @route('/image/<dataset>/add', methods=['POST'])
    def create_image(self, dataset):
        (ok, error, image) = view_tools.get_image_from_request(request)
        if not ok:
            raise error_views.InvalidParametersError(error)

        (ok, error, category) = view_tools.get_param_from_request(request, "category")
        if not ok or category == "":
            category = "default"

        (ok, error, name) = view_tools.get_param_from_request(request, "name")
        if not ok:
            name = ""

        (ok, error, image_id) = self.controller.create_image(dataset, image, category=category, name=name)
        if not ok:
            raise error_views.InvalidParametersError(error)

        image_url = "{}/{}".format(dataset, image_id)
        return flask.jsonify({"imageId": image_id,
                                "imageUrl": image_url})
