from annotator_supreme import app
from annotator_supreme.controllers import database_controller
import time, datetime


TABLE = "users"

class User():

    def __init__(self, username, password_hash, email, points = 0, registration_date = None):
        self.username = username
        self.password_hash = password_hash
        self.email = email
        self.points = points

        if registration_date is None:
            self.registration_date = datetime.datetime.now()
        else:
            self.registration_date = registration_date

        with app.app_context():
            self.db_session = database_controller.get_db(app.config)

    @classmethod
    def from_username(cls, username):
        with app.app_context():
            db_session = database_controller.get_db(app.config)
            cql = "SELECT username, " + \
                        "password_hash, " + \
                        "email, " + \
                        "points, " + \
                        "registration_date FROM "+TABLE+" WHERE username=\'"+username+"\'"
            rows = db_session.execute(cql)
            rows = list(rows)

            if len(rows) == 0:
                return None
            elif len(rows) == 1:
                r = rows[0]
                return cls(r.username, r.password_hash, r.email, r.points, r.registration_date)
            elif len(rows) > 1:
                app.logger.warning('Query error: the same username cannot appear twice.')
                return None

    def upsert(self):
        cql = self.db_session.prepare(\
            "INSERT INTO "+TABLE+" (username, password_hash, email, points, registration_date) "+\
            "VALUES (?,?,?,?,?)")
        self.db_session.execute(cql, [self.username, self.password_hash, self.email, self.points, self.registration_date])

    def is_authenticated(self):
        return True
 
    def is_active(self):
        return True
 
    def is_anonymous(self):
        return False
 
    def get_id(self):
        return self.username