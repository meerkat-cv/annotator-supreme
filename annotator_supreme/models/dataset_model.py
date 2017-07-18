from annotator_supreme import app
from annotator_supreme.controllers import database_controller
import time

TABLE = "datasets"

class DatasetModel():

    def __init__(self, dataset_name, tags = [], annotation_labels = [], image_categories = []):
        self.dataset_name = dataset_name
        self.tags = tags
        if annotation_labels is None:
            self.annotation_labels = []
        else:
            self.annotation_labels = annotation_labels
        if image_categories is None:
            self.image_categories = []
        else:
            self.image_categories = image_categories
        with app.app_context():
            self.db_session = database_controller.get_db(app.config)

    @classmethod
    def from_name(cls, dataset_name):
        with app.app_context():
            db_session = database_controller.get_db(app.config)
            cql = "SELECT name, " + \
                        "tags, " + \
                        "annotation_labels, " + \
                        "image_categories, " + \
                        "last_modified FROM "+TABLE+" WHERE name=\'"+dataset_name+"\'"
            rows = db_session.execute(cql)
            rows = list(rows)

            if len(rows) == 0:
                app.logger.warning('Did not found doc with the provided dataset.')
                return None
            elif len(rows) == 1:
                r = rows[0]
                return cls(r.name, r.tags, r.annotation_labels, r.image_categories)
            elif len(rows) > 1:
                app.logger.warning('Query error: the same dataset cannot appear twice.')
                return None

    def upsert(self):
        cql = self.db_session.prepare(
            """
            INSERT INTO datasets (name, tags, annotation_labels, image_categories, last_modified)
            VALUES (?, ?, ?, ?, ?)
            """)
        self.db_session.execute(cql, [self.dataset_name, self.tags, self.annotation_labels, self.image_categories, int(time.time())])


    def delete(self):
        with app.app_context():
            db_session = database_controller.get_db(app.config)
            
            cql = "DELETE FROM "+TABLE+" WHERE name=\'"+self.dataset_name+"\'" 
            res = db_session.execute(cql)
            
            return (True, "")

    def add_annotation_labels(self, label):
        self.annotation_labels.append(label)
        self.upsert()

    def add_image_category(self, category):
        self.image_categories.append(category)
        self.upsert()

    @staticmethod
    def list_datasets():
        with app.app_context():
            db_session = database_controller.get_db(app.config)
            rows = db_session.execute("SELECT name, tags, annotation_labels, image_categories, last_modified FROM "+TABLE)
            return list(rows)

