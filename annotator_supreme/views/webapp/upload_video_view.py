import flask
from flask.ext.classy import FlaskView, route, request
from annotator_supreme.views.view_tools import *
from annotator_supreme import app
from annotator_supreme.controllers.dataset_controller import DatasetController
from annotator_supreme.controllers.image_controller import ImageController
from flask import render_template
from werkzeug.utils import secure_filename

class UploadVideoViewWebApp(FlaskView):
    route_base = '/'

    def __init__(self):
        self.dataset_controller = DatasetController()
        self.image_controller = ImageController()

    @route('/add/video', methods=['GET'])
    def datasets(self):
        datasets = self.dataset_controller.get_datasets()
        return render_template('upload_video.html', datasets=datasets)

    def allowed_file(self, filename):
        ALLOWED_EXTENSIONS = set(['bmp', 'png', 'jpg', 'jpeg', 'gif'])
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

    def get_frontend_image(self, request):
        file = request.files['file']
        filename = secure_filename(file.filename)
        file.save(os.path.join('/tmp/', filename))

        # load from file and read image
        try:
            image = cv2.imread(os.path.join('/tmp/', filename))
            return image
        except:
            raise error_views.InternalError('Unable to read image from local folder.')



    @route('/video/front-upload', methods=['POST'])
    def create_video(self):
        file = request.files['file']
        if file and self.allowed_file(file.filename):
            if 'dataset' not in request.form:
                raise error_views.InternalError('No dataset provided!')    
            dataset_name = request.form['dataset']

            category = 'default'
            if 'category' in request.form:
                category = request.form['category']

            image = self.get_frontend_image(request)
            (ok, error, image_id) = self.image_controller.create_image(dataset_name, image, name=file.filename, category=category)
            if not ok:
                raise error_views.InvalidParametersError(error)

            return '', 200
        else:
            raise error_views.InternalError('The provided file is not an accepted extension.')
