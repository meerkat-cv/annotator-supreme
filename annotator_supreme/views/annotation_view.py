import flask
from flask.ext.classy import FlaskView, route, request
from annotator_supreme.models.bbox_model import BBox
from annotator_supreme.controllers.image_controller import ImageController
from annotator_supreme.views import view_tools
from annotator_supreme.views import error_views
from annotator_supreme import app
import cv2

class AnnoView(FlaskView):
    route_base = '/'

    def __init__(self):
        self.controller = ImageController()

    @route('/image/anno/<dataset>/<imageid>', methods=['GET'])
    def get_image_anno(self, dataset, imageid):
        image = self.controller.get_image_object(dataset, imageid)
        image_dict = view_tools.image_to_dict(image)

        return flask.jsonify(image_dict)

    def paginate(self, list, page_number, page_size):
        start_elem = page_size * (page_number - 1)

        return list[start_elem:start_elem+page_size]

    @route('/image/anno/<dataset>/all', methods=['GET'])
    def get_all_dataset_anno(self, dataset):
        all_images = ImageController.all_images(dataset)
    
        all_annotations = []
        for img in all_images:
            app.logger.info("img: "+str(img["annotation"]))
            for i, anno in enumerate(img["annotation"]):
                d = {
                    "top": anno.top,
                    "bottom": anno.bottom,
                    "left": anno.left,
                    "right": anno.right,
                    "labels": anno.labels,
                    "ignore": anno.ignore,
                    "image_url": img["url"],
                    "anno_ith": i
                }
                all_annotations.append(d)
            

        ok_pagesize, _, page_size = view_tools.get_param_from_request(request, 'itemsPerPage')
        ok_page, _, page_number = view_tools.get_param_from_request(request, 'pageNumber')

        if ok_pagesize and ok_page:
            return flask.jsonify({
                "annotations": self.paginate(all_annotations, int(page_number), int(page_size)),
                "pageNumber": int(page_number),
                "itemsPerPage": int(page_size),
                "totalPages": len(all_annotations)//int(page_size)})
        else:
            return flask.jsonify({"annotations": all_annotations})

    @route('/image/has_annotation/<dataset>/<imageid>', methods=['GET'])
    def get_image_has_anno(self, dataset, imageid):
        image = self.controller.get_image_details(dataset, imageid)
        
        return flask.jsonify({"has_annotation": image["has_annotation"]})


    @route('/image/anno/<dataset>/<imageid>', methods=['POST'])
    def post_image_anno(self, dataset, imageid):
        """
        Parameters:
        - anno: a list of bounding boxes 
        - scale: optional
        """
        (ok, error, anno) = view_tools.get_param_from_request(request, 'anno')

        (ok_scale, _, scale) = view_tools.get_param_from_request(request, 'scale')

        try:
            bbs_vec = []
            for bb in anno:
                bbox_o = BBox(bb['top'], bb['left'], bb['bottom'], bb['right'], bb['labels'], bb['ignore'])
                if ok_scale and scale != 1.0:
                    bbox_o.scale_itself(scale)
                bbs_vec.append(bbox_o)
        except BaseException as e:
            print('Problem with provided annotation', anno, str(e))
            return 'Problem with provided annotation',500

        self.controller.change_annotations(dataset, imageid, bbs_vec)

        return '', 200