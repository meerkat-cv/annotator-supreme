import flask
from flask.ext.classy import FlaskView, route, request
from annotator_supreme.controllers.user_controller import UserController
from annotator_supreme.views import view_tools
from annotator_supreme.views import error_views
from flask import render_template, flash, redirect, url_for
from annotator_supreme import app
from flask.ext.login import login_user, logout_user
import json

class LoginViewWebApp(FlaskView):
    route_base = '/'

    def __init__(self):
        self.user_controller = UserController()

    @route('/register' , methods=['GET','POST'])
    def register_user(self):
        if request.method == 'GET':
            return render_template('register.html')
        elif request.method == 'POST':
            app.logger.info("Got post")
            app.logger.info(request.form)

            username, password, email = request.form['username'] , request.form['password'], request.form['email']
            ok, error = self.user_controller.create_user(username, password, email)
            if ok:
                return "", 200
            else:
                return "User already registered", 432
 
    @route('/login',methods=['GET','POST'])
    def login(self):
        if request.method == 'GET':
            return render_template('login.html')
        elif request.method == 'POST':            
            username = request.form['username']
            password = request.form['password']
            user = self.user_controller.get_user_w_password(username, password)
            if user is None:
                return "Invalid credentials", 432
            else:
                login_user(user)
                return "", 200

    @route('/logout', methods=['GET'])
    def logout(self):
        logout_user()
        return "", 200
        

