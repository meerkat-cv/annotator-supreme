import traceback
import flask
import json
from flask.ext.classy import FlaskView, route, request
from annotator_supreme.views.view_tools import *
from annotator_supreme import app
from annotator_supreme._version import __version__
from annotator_supreme.controllers.image_controller import *
from flask import render_template

class ImageTestViewWebApp(FlaskView):
    route_base = '/'

    def __init__(self):
        self.controller = ImageController()

    @route('/image/page', methods=['GET'])
    def image_page_get(self):
        return render_template('image_test.html')


    @route('/image/<dataset>', methods=['GET'])
    def image_get(self, dataset):
        all_imgs = self.controller.all_images(dataset)

        im_src = "/annotator-supreme/static/meerkat/images/im_01.jpg"
        try:
            curr_im = int(request.args['page'])
            curr_im = (curr_im % 4) + 1
            im_src = "/annotator-supreme/static/meerkat/images/im_0"+str(curr_im)+".jpg"
        except BaseException as e:
            print('Exception:',str(e))
            traceback.print_exc()
        return json.dumps({'im': im_src})
