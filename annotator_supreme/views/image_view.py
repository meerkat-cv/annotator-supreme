import flask
from flask.ext.classy import FlaskView, route, request
from annotator_supreme.models.bbox_model import BBox
from annotator_supreme.controllers.image_controller import ImageController
from annotator_supreme.views import view_tools
from annotator_supreme.views import error_views
import cv2

class ImageView(FlaskView):
    route_base = '/'

    def __init__(self):
        self.controller = ImageController()

    @route('/image/<dataset>/<imageid>', methods=['GET'])
    def get_image(self, dataset, imageid):
        img = self.controller.get_image(dataset, imageid)
        fileid = "img" # uuid.uuid4().hex
        full_filename = 'annotator_supreme/static/'+fileid+'.jpg'
        cv2.imwrite(full_filename, img)
        filename = 'static/'+fileid+'.jpg'

        return flask.send_file(filename, mimetype='image/jpeg')


    @route('/image/anno/<dataset>/<imageid>', methods=['GET'])
    def get_image_anno(self, dataset, imageid):
        anno = self.controller.get_image_anno(dataset, imageid)
        anno_dict = self.anno_to_dict(anno)

        return flask.jsonify(anno_dict)

    def anno_to_dict(self, anno):
        anno_vec = []
        for bb in anno:
            curr_anno = {}
            curr_anno['labels'] = bb.labels
            curr_anno['left']   = bb.left
            curr_anno['top']    = bb.top
            curr_anno['right']  = bb.right
            curr_anno['bottom'] = bb.bottom
            curr_anno['ignore'] = bb.ignore
            anno_vec.append(curr_anno)

        anno_dict = {'anno': anno_vec}

        return anno_dict

    @route('/image/anno/<dataset>/<imageid>', methods=['POST'])
    def post_image_anno(self, dataset, imageid):
        (ok, error, anno) = view_tools.get_param_from_request(request, 'anno')

        try:
            bbs_vec = []
            for bb in anno:
                bbox_o = BBox(bb['top'], bb['left'], bb['bottom'], bb['right'], bb['labels'], bb['ignore'])
                bbs_vec.append(bbox_o)
        except BaseException as e:
            print('Problem with provided annotation', anno, str(e))
            return 'Problem with provided annotation',500

        self.controller.change_annotations(dataset, imageid, bbs_vec)

        return '',200

    @route('/image/<dataset>/all', methods=['GET'])
    def get_all_images(self, dataset):
        print('dataset', dataset)

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
