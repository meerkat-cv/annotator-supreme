import flask
from io import BytesIO
from flask.ext.classy import FlaskView, route, request
from annotator_supreme.models.bbox_model import BBox
from annotator_supreme.controllers.image_controller import ImageController
from annotator_supreme.controllers.image_utils import ImageUtils
from annotator_supreme.views import view_tools
from annotator_supreme.views import error_views
from annotator_supreme import app
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
        ret, img_bin = cv2.imencode(".jpg", img)
        return flask.send_file(BytesIO(img_bin), mimetype='image/jpeg')


    @route('/image/thumb/<dataset>/<imageid>', methods=['GET'])
    def get_image_thumb(self, dataset, imageid):
        img = self.controller.get_image(dataset, imageid)
        img_o = self.controller.get_image_object(dataset, imageid)
        thumb = ImageUtils.create_thumbnail(img, img_o)
        ret, img_bin = cv2.imencode(".jpg", thumb)
        return flask.send_file( BytesIO(img_bin) , mimetype='image/jpeg')

    @route('/image/cropanno/<dataset>/<imageid>/<annotation_i>', methods=['GET'])
    def get_image_annotation_cropped(self, dataset, imageid, annotation_i):
        img = self.controller.get_image(dataset, imageid)
        img_o = self.controller.get_image_object(dataset, imageid)
        
        if int(annotation_i) < len(img_o.bboxes):
            cropped_annotation = ImageUtils.crop_image(img, img_o.bboxes[int(annotation_i)])
        else:
            cropped_annotation = img
        
        ret, img_bin = cv2.imencode(".jpg", cropped_annotation)
        return flask.send_file(BytesIO(img_bin), mimetype='image/jpeg')

    def paginate(self, list, page_number, page_size):
        start_elem = page_size * (page_number - 1)

        return list[start_elem:start_elem+page_size]


    @route('/image/<dataset>/all', methods=['GET'])
    def get_all_images(self, dataset):

        all_images = ImageController.all_images(dataset)
        ok_pagesize, _, page_size = view_tools.get_param_from_request(request, 'itemsPerPage')
        ok_page, _, page_number = view_tools.get_param_from_request(request, 'pageNumber')

        if ok_pagesize and ok_page:
            return flask.jsonify({
                "images": self.paginate(all_images, int(page_number), int(page_size)),
                "pageNumber": int(page_number),
                "itemsPerPage": int(page_size),
                "totalPages": len(all_images)//int(page_size)})
        else:
            return flask.jsonify({"images": all_images})

    @route('/image/<dataset>/annotated', methods=['GET'])
    def get_annotated_images(self, dataset):

        all_images = ImageController.all_images(dataset)
        app.logger.info('all_images'+str(all_images))
        annotated = [im for im in all_images if len(im["annotation"]) > 0]
        ok_pagesize, _, page_size = view_tools.get_param_from_request(request, 'itemsPerPage')
        ok_page, _, page_number = view_tools.get_param_from_request(request, 'pageNumber')

        if ok_pagesize and ok_page:
            return flask.jsonify({
                "images": self.paginate(annotated, int(page_number), int(page_size)),
                "pageNumber": int(page_number),
                "itemsPerPage": int(page_size),
                "totalPages": len(annotated)//int(page_size)})
        else:
            return flask.jsonify({"images": annotated})


    @route('/image/<dataset>/unannotated', methods=['GET'])
    def get_annotated_images(self, dataset):

        all_images = ImageController.all_images(dataset)
        app.logger.info('all_images'+str(all_images))
        unannotated = [im for im in all_images if len(im["annotation"]) == 0]
        ok_pagesize, _, page_size = view_tools.get_param_from_request(request, 'itemsPerPage')
        ok_page, _, page_number = view_tools.get_param_from_request(request, 'pageNumber')

        if ok_pagesize and ok_page:
            return flask.jsonify({
                "images": self.paginate(unannotated, int(page_number), int(page_size)),
                "pageNumber": int(page_number),
                "itemsPerPage": int(page_size),
                "totalPages": len(unannotated)//int(page_size)})
        else:
            return flask.jsonify({"images": unannotated})

    
    @route('/image/<dataset>/add', methods=['POST'])
    def create_image(self, dataset):
        """
        Add and image to the dataset 
        ---
        parameters:
        - name: the name of the image 
        - category: a name of the category
        - image: multi-part from data
        """

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
