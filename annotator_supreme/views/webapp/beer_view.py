import flask
from flask.ext.classy import FlaskView, route, request
from annotator_supreme.controllers.user_controller import UserController
from annotator_supreme.views import view_tools
from annotator_supreme.views import error_views
from flask import render_template, flash, redirect, url_for
from annotator_supreme import app
from flask.ext.login import login_user, logout_user, current_user
import json

BEER_PRICE = 100

class BeerViewWebApp(FlaskView):
    route_base = '/'


    def __init__(self):
        self.user_controller = UserController()

    def compute_beer_count(self):
        points = current_user.points
        return points//BEER_PRICE

    def compute_next_beer_percentage(self):
        points = current_user.points
        if points > 0:
            return (points % BEER_PRICE)/BEER_PRICE
        else:
            return 0

    @route("/beer_count", methods=["GET"])
    def get_beer(self):
        d = {
            "total_beer": self.compute_beer_count(),
            "next_beer_percentage": self.compute_next_beer_percentage()
        }

        return flask.jsonify(d)

    @route("/add/points/<username>/<points>", methods=["GET"])
    def add_beer_points(self, username, points):
        self.user_controller.add_points(username, int(points))

        return "",200



