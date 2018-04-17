import flask
import base64
import importlib
from flask.ext.classy import FlaskView, route, request
from annotator_supreme.controllers.plugins_controller import PluginsController
from annotator_supreme.controllers.image_controller import ImageController
from annotator_supreme.controllers.dataset_controller import DatasetController
from annotator_supreme.views import view_tools
from annotator_supreme.views import error_views
from annotator_supreme.models.bbox_model import BBox
import cv2
import logging

class PluginsView(FlaskView):
    route_base = '/'

    def __init__(self):
        self.logger = logging.getLogger('annotator_supreme.views.plugins')
        
        self.controller = PluginsController()
        self.image_controller = ImageController()
        self.dataset_controller = DatasetController()

    @route('/plugins/process/<dataset>/<imageid>', methods=['GET', 'POST'])
    def get_plugin_process_image(self, dataset, imageid):
        self.get_plugin_from_request(request)

        if request.method == 'POST':
            self.controller.init_plugin(self.dataset_controller.get_dataset(dataset), additional_params=request.get_json().get("additional_params", {}))
        elif request.method == 'GET':
            self.controller.init_plugin(self.dataset_controller.get_dataset(dataset))

        (img_m, img_o) = self.get_image_matrix_and_dict(dataset, imageid)
        (img_m, img_o) = self.controller.process(img_m, img_o)
        plugin_res = self.controller.end_plugin()

        fileid = "img" # uuid.uuid4().hex
        full_filename = 'annotator_supreme/static/'+fileid+'.jpg'
        cv2.imwrite(full_filename, img_m)
        filename = 'static/'+fileid+'.jpg'

        # return flask.send_file(filename, mimetype='image/jpeg')
        img_bytes = cv2.imencode('.jpg', img_m)[1].tostring()
        img_encoded = base64.b64encode(img_bytes).decode()

        return flask.jsonify({'image': img_encoded, 'plugin_response': plugin_res})


    @route('/plugins/process/<dataset>', methods=['GET', 'POST'])
    def get_plugin_process(self, dataset):
        self.get_plugin_from_request(request)
        
        if request.method == 'POST':
            self.controller.init_plugin(self.dataset_controller.get_dataset(dataset), additional_params=request.get_json().get("additional_params", {}))
        elif request.method == 'GET':
            self.controller.init_plugin(self.dataset_controller.get_dataset(dataset))

        all_imgs = ImageController.all_images(dataset)
        for im_obj in all_imgs:
            (img_m, img_o) = self.get_image_matrix_and_dict(dataset, im_obj['phash'])
            (img_m, img_o) = self.controller.process(img_m, img_o)
            bbs_vec = []
            for bb in img_o['anno']:
                bbox_o = BBox(bb['top'], bb['left'], bb['bottom'], bb['right'], bb['labels'], bb['ignore'])
                bbs_vec.append(bbox_o)
            self.image_controller.change_annotations(dataset, img_o['phash'], bbs_vec)
        
        plugin_res = self.controller.end_plugin()
        return flask.jsonify({"plugin_response": plugin_res})


    @route('/plugins/process/partition/<dataset>/<partition>', methods=['GET'])
    def get_plugin_process_partition(self, dataset, partition):
        self.get_plugin_from_request(request)

        if partition == "" or (partition != "training" and partition != "testing"):
            raise error_views.InvalidParametersError("Partition not informed or invalid.")
        

        if request.method == 'POST':
            self.controller.init_plugin(self.dataset_controller.get_dataset(dataset), partition, additional_params=request.get_json().get("additional_params", {}))
        elif request.method == 'GET':
            self.controller.init_plugin(self.dataset_controller.get_dataset(dataset), partition)

        all_imgs = ImageController.all_images(dataset)
        for im_obj in all_imgs:
            (img_m, img_o) = self.get_image_matrix_and_dict(dataset, im_obj['phash'])
            (img_m, img_o) = self.controller.process(img_m, img_o)
            bbs_vec = []
            for bb in img_o['anno']:
                bbox_o = BBox(bb['top'], bb['left'], bb['bottom'], bb['right'], bb['labels'], bb['ignore'])
                bbs_vec.append(bbox_o)
            self.image_controller.change_annotations(dataset, img_o['phash'], bbs_vec)
    
        plugin_res = self.controller.end_plugin()
        return flask.jsonify({"plugin_response": plugin_res})


    @route('/plugins/all', methods=['GET'])
    def get_plugin_all(self):
        plugins = self.controller.get_all_plugins()
        return flask.jsonify({"plugins": sorted(plugins)})


    def get_plugin_from_request(self, request):
        (ok, error, plugin_name) = view_tools.get_param_from_request(request, 'plugin')
        if not ok:
            raise error_views.InvalidParametersError(error)

        ok = self.controller.load_plugin(plugin_name)
        if not ok:
            self.logger.error('An error occurred while loading plugin: %s', plugin_name)
            raise error_views.InternalError('An error occurred while loading plugin: '+ plugin_name)


    def get_image_matrix_and_dict(self, dataset, imageid):
        img = self.image_controller.get_image(dataset, imageid)
        img_o = self.image_controller.get_image_object(dataset, imageid)
        img_d = view_tools.image_to_dict(img_o)

        return (img, img_d)
