
from flask import Flask, jsonify, session
from flask.ext.cors import CORS
from flask_swagger import swagger
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

def setup_views():
    from annotator_supreme.views.version_view import VersionView

    app.logger.info('Registering views')
    VersionView.register(app)
    app.logger.info('done.')

    app.wsgi_app = ProxyFix(app.wsgi_app)
    app.debug = app.config["APP_DEBUG"]


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

    # we define an app secret key to keep session variables secure
    app.secret_key = '6869fab6ae6e276e7f6e1c3fcf5253ca'

    # seting the logger using the flask
    logging.basicConfig(format='annotator-supreme: %(asctime)s - %(levelname)s - %(message)s')
    app.logger.setLevel(app.config["LOG_LEVEL"])
    app.logger.info('annotator-supreme - The most awesome annotator and provider of CV datasets.')

    from annotator_supreme.controllers.base_controller import ReverseProxied
    app.wsgi_app = ReverseProxied(app.wsgi_app)

    setup_views()

    tr = WSGIContainer(app)
    tornado_application = tornado.web.Application(
    [
        (r".*", FallbackHandler, dict(fallback=tr))
    ])
    app.logger.info('done.')
    app.logger.info('App built successfully!')

    return tornado_application
