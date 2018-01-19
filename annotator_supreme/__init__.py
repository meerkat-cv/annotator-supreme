
from flask import Flask, jsonify, session
from flask.ext.cors import CORS
from werkzeug.contrib.fixers import ProxyFix
import logging
import os
import sys
import json
from flask import g
from tornado.web import FallbackHandler, RequestHandler, Application
from tornado.wsgi import WSGIContainer
import tornado

instance_path = os.path.dirname(os.path.realpath(__file__)) + '/config/'
app = Flask(__name__, instance_relative_config=True, instance_path=instance_path)
db_global = None

def setup_views():
    from annotator_supreme.views.version_view import VersionView
    from annotator_supreme.views.dataset_view import DatasetView
    from annotator_supreme.views.image_view import ImageView
    from annotator_supreme.views.image_edit_view import ImageEditView
    from annotator_supreme.views.annotation_view import AnnoView
    from annotator_supreme.views.plugins_view import PluginsView
    from annotator_supreme.views.webapp.image_test import ImageTestViewWebApp
    from annotator_supreme.views.webapp.annotation_view import AnnotationViewWebApp
    from annotator_supreme.views.webapp.dataset_view import DatasetViewWebApp
    from annotator_supreme.views.webapp.plugins_view import PluginsViewWebApp
    from annotator_supreme.views.webapp.upload_video_view import UploadVideoViewWebApp
    from annotator_supreme.views.webapp.upload_view import UploadViewWebApp
    from annotator_supreme.views.webapp.visualize_images_view import VisualizeImagesViewWebApp
    from annotator_supreme.views.webapp.login_view import LoginViewWebApp
    from annotator_supreme.views.webapp.beer_view import BeerViewWebApp

    VersionView.register(app)
    AnnoView.register(app)
    DatasetView.register(app)
    ImageView.register(app)
    ImageEditView.register(app)
    PluginsView.register(app)
    ImageTestViewWebApp.register(app)
    AnnotationViewWebApp.register(app)
    DatasetViewWebApp.register(app)
    PluginsViewWebApp.register(app)
    UploadViewWebApp.register(app)
    UploadVideoViewWebApp.register(app)
    VisualizeImagesViewWebApp.register(app)
    LoginViewWebApp.register(app)
    BeerViewWebApp.register(app)
    # app.wsgi_app = ProxyFix(app.wsgi_app)

def build_app():
    server_env = os.getenv('SERVER_ENV')
    if server_env is not None:
        server_env = server_env.lower().strip()
    envs = {'production': 'production.py', 'development': 'development.py', 'on_premise': 'premise.py'}

    env_file = ''
    if server_env is None or server_env not in envs.keys():
        logging.warning(
            'No SERVER_ENV variable found. Assuming development...')
        env_file = envs['development']
        server_env = 'development'
    else:
        env_file = envs[server_env]

    app.config.from_pyfile(env_file)
    CORS(app)

    CLUSTER_IP = os.getenv("CLUSTER_IP")
    if CLUSTER_IP is None:
        app.config["CLUSTER_IP"] = "127.0.0.1"
    else:
        app.config["CLUSTER_IP"] = CLUSTER_IP

    # we define an app secret key to keep session variables secure
    app.secret_key = '6869fab6ae6e276e7f6e1c3fcf5253ca'

    # seting the logger using the flask

    # logging.basicConfig(format='annotator-supreme: %(asctime)s - %(levelname)s - %(message)s')
    app.debug = app.config["APP_DEBUG"]

    fmt = '%(levelname)s - [%(asctime)s] - %(name)s : %(message)s'
    formatter = logging.Formatter(fmt)

    app.logger.setLevel(app.config["LOG_LEVEL"])

    # Bug?? the lines bellow actually duplicate the logging
    #for handler in app.logger.handlers:
    #    app.logger.warning("Changing handler: %s",handler)
    #    handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    for handler in root_logger.handlers:
        app.logger.warning("ROOT HANDLER: %s",handler)
        handler.setFormatter(formatter)

    app.logger.info("Setting up database (Cassandra)...")
    
    from annotator_supreme.controllers import database_controller
    db_controller = database_controller.DatabaseController()
    db_controller.setup_database()
    app.logger.info('DB Controller done.')

    # from annotator_supreme.controllers.base_controller import ReverseProxied
    # app.wsgi_app = ReverseProxied(app.wsgi_app)

    app.logger.info('Registering views')
    setup_views()
    
    app.logger.info('done.')
    app.logger.info('App %s built successfully!', __name__)

    app.logger.info('annotator-supreme - The most awesome annotator and provider of CV datasets.')
    app.logger.info('app.debug = %s', app.debug)
    

    return app
