from annotator_supreme import app
from annotator_supreme.controllers import database_controller

TABLE = "datasets"

class DatasetModel():

    def __init__(self, dataset_name, tags):
        self.dataset_name = dataset_name
        self.tags = tags
        with app.app_context():
            self.db_session = database_controller.get_db(app.config)

    def upsert(self):
        self.db_session.execute(
            """
            INSERT INTO datasets (name, tags)
            VALUES (%s, %s)
            """,
            (self.dataset_name, self.tags)
        )

    @staticmethod
    def list_datasets():
        with app.app_context():
            db_session = database_controller.get_db(app.config)
            rows = db_session.execute('SELECT name, tags FROM '+TABLE)
            # print("rows from db: ", rows)
            # print("rows from db: ", list(rows))
            return list(rows)