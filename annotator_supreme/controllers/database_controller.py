from annotator_supreme import app
from flask import g
from cassandra.cluster import Cluster




def get_db(config):
    """
    This functions connect to the Cassandra database and kept in the flask app
    """
    with app.app_context():
        db = getattr(g, '_database', None)
        if db is None:
            start_time = time.time()
            db = g._database = Bucket(config['COUCHBASE_HOST'])
        return db