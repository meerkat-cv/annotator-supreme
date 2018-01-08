from annotator_supreme.models.user_model import User
import bcrypt
from annotator_supreme import app

class UserController():

    def __init__(self):
        pass

    def create_user(self, username, password, email):
        app.logger.info(type(password))
        if not self.user_exists(username):
            # We're not the BB or ZH to save the password plain-text.
            b_password = password.encode()
            password_hash = bcrypt.hashpw(b_password, bcrypt.gensalt())
            user = User(username, password_hash.decode(), email)
            user.upsert()

            return True, ""
        else:
            return False, "Already registered user"

    def get_user_w_password(self, username, password):
        if self.user_exists(username):
            # attempt_password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt())

            user = User.from_username(username)
            if bcrypt.checkpw(password.encode(), user.password_hash.encode()):
                return user
            else:
                return None
        else:
            # username does not exists, but dont tell anyone
            return None

    def user_exists(self, username):
        return User.from_username(username) != None

# should configure flask-login upon start
from flask.ext.login import LoginManager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
@login_manager.user_loader
def load_user(user_id):
    return User.from_username(user_id)