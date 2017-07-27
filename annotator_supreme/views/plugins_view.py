import flask
import base64
import importlib
from flask.ext.classy import FlaskView, route, request
from annotator_supreme.controllers.plugins_controller import PluginsController
from annotator_supreme.controllers.image_controller import ImageController
from annotator_supreme.controllers.dataset_controller import DatasetController
from annotator_supreme.views import view_tools
from annotator_supreme.views import error_views
import cv2

class PluginsView(FlaskView):
    route_base = '/'

    def __init__(self):
        self.controller = PluginsController()
        self.image_controller = ImageController()
        self.dataset_controller = DatasetController()

    @route('/plugins/process/<dataset>/<imageid>', methods=['GET'])
    def get_plugin_process_image(self, dataset, imageid):
        self.get_plugin_from_request(request)

        self.controller.init_plugin(self.dataset_controller.get_dataset(dataset))

        (img, anno) = self.get_image_and_anno(dataset, imageid)
        (img, anno) = self.controller.process(img, anno)
        plugin_res = self.controller.end_plugin()

        fileid = "img" # uuid.uuid4().hex
        full_filename = 'annotator_supreme/static/'+fileid+'.jpg'
        cv2.imwrite(full_filename, img)
        filename = 'static/'+fileid+'.jpg'

        # return flask.send_file(filename, mimetype='image/jpeg')
        img_bytes = cv2.imencode('.jpg', img)[1].tostring()
        img_encoded = base64.b64encode(img_bytes).decode()

        return flask.jsonify({'image': img_encoded, 'plugin_response': plugin_res})


    @route('/plugins/process/<dataset>', methods=['GET'])
    def get_plugin_process(self, dataset):
        self.get_plugin_from_request(request)
        
        self.controller.init_plugin(self.dataset_controller.get_dataset(dataset))

        all_imgs = ImageController.all_images(dataset)
        for im_obj in all_imgs:
            (img, anno) = self.get_image_and_anno(dataset, im_obj['phash'])
            (img, anno) = self.controller.process(img, anno)
        
        plugin_res = self.controller.end_plugin()
        return flask.jsonify({"plugin_response": plugin_res})


    @route('/plugins/process/partition/<dataset>/<partition>', methods=['GET'])
    def get_plugin_process_partition(self, dataset, partition):
        self.get_plugin_from_request(request)

        if partition == "" or (partition != "training" and partition != "testing"):
            raise error_views.InvalidParametersError("Partition not informed or invalid.")
        
        self.controller.init_plugin(self.dataset_controller.get_dataset(dataset))

        all_imgs = ImageController.all_images(dataset)
        for im_obj in all_imgs:
            if im_obj['partition'] == DatasetController.partition_id(partition):
                (img, anno) = self.get_image_and_anno(dataset, im_obj['phash'])
                (img, anno) = self.controller.process(img, anno)
        
        plugin_res = self.controller.end_plugin()
        return flask.jsonify({"plugin_response": plugin_res})


    @route('/plugins/all', methods=['GET'])
    def get_plugin_all(self):
        plugins = self.controller.get_all_plugins()
        return flask.jsonify({"plugins": plugins})


    def get_plugin_from_request(self, request):
        (ok, error, plugin_name) = view_tools.get_param_from_request(request, 'plugin')
        if not ok:
            raise error_views.InvalidParametersError(error)

        ok = self.controller.load_plugin(plugin_name)
        if not ok:
            print('An error occurred while loading plugin: '+ plugin_name)
            raise error_views.InternalError('An error occurred while loading plugin: '+ plugin_name)


    def get_image_and_anno(self, dataset, imageid):
        img = self.image_controller.get_image(dataset, imageid)
        anno_obj = self.image_controller.get_image_anno(dataset, imageid)
        anno = view_tools.anno_to_dict(anno_obj)

        return (img, anno)
