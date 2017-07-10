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


    @route('/image/<dataset>/<imageid>', methods=['GET'])
    def get_image(self, dataset, imageid):
        img = self.controller.get_image(dataset, imageid)
        fileid = "img" # uuid.uuid4().hex
        full_filename = 'annotator_supreme/static/'+fileid+'.jpg'
        cv2.imwrite(full_filename, img)
        filename = 'static/'+fileid+'.jpg'

        return flask.send_file(filename, mimetype='image/jpeg')

    def resize4thumb(self, img):
        if img.shape[0] < img.shape[1]:
            factor = 200./img.shape[0]
            # make height 200, and width accordantly
            img = cv2.resize(img, (int(img.shape[1]*factor), 200))
            # get only the center portion of image
            w = img.shape[1]
            return img[:, (w-200)//2:(w+200)//2, :]
        else:
            factor = 200./img.shape[1]
            # make height 200, and width accordantly
            img = cv2.resize(img, (200, int(img.shape[0]*factor)))
            # get only the center portion of image
            h = img.shape[0]
            return img[(h-200)//2:(h+200)//2, :, :]


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

        (ok, error, image_id) = self.controller.create_image(dataset, image)
        if not ok:
            raise error_views.InvalidParametersError(error)

        image_url = "{}/{}".format(dataset, image_id)
        return flask.jsonify({"imageId": image_id,
                                "imageUrl": image_url})
