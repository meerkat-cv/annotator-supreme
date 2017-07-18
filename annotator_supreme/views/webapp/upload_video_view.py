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
        ALLOWED_EXTENSIONS = set(['mov', 'mpeg', 'mp4', 'mpg', 'avi'])
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

    def extract_frontend_frames(self, request, step_frame):
        file = request.files['file']
        filename = secure_filename(file.filename)
        file.save(os.path.join('/tmp/', filename))

        vid = cv2.VideoCapture(os.path.join('/tmp/', filename))
        if not vid.isOpened():
            raise error_views.InternalError("Not possible to open video file.")
        else:
            frames = []
            ret, frame = vid.read()
            i = 0
            while frame is not None:
                if i % step_frame == 0:
                    # save it as base64 image
                    img_bytes = cv2.imencode('.jpg', frame)[1]
                    img_encoded = base64.b64encode(img_bytes).decode()
                    frames.append(img_encoded)

                i = i + 1
                ret, frame = vid.read()
        vid.release()

        return frames

    @route('/video/front-upload', methods=['POST'])
    def create_video(self):
        file = request.files['file']
        if file and self.allowed_file(file.filename):
            if 'step_frame' in request.form:
                step_frame = int(request.form['step_frame'])
            else:
                app.logger("Step frame not provided, assuming 10.")
                step_frame = 10

            frames = self.extract_frontend_frames(request, step_frame)
            if not frames:
                raise error_views.InternalError("Unable to extract frames from the video file.")

            return flask.jsonify({"frames_b64": frames})
        else:
            raise error_views.InternalError('The provided file is not an accepted extension.')

