from annotator_supreme import app
from annotator_supreme.controllers import database_controller
import time, datetime

from enum import Enum

# There are different types of reference count and our model puts together
# all of them to simplify access, but the tables are separated
class RefCountType(Enum):
    CATEGORY = 0
    LABEL = 1


class RefCountModel():

    def __init__(self, dataset, name, ref_type, ref_count = 0):
        self.dataset = dataset
        self.name = name # this will be a label/category/other
        self.type = ref_type
        self.ref_count = ref_count
        self.db_session = database_controller.get_db(app.config)

    @classmethod
    def from_label(cls, dataset, label):
        TABLE = "label_ref_count"
        with app.app_context():
            db_session = database_controller.get_db(app.config)
            cql = "SELECT dataset, " + \
                            "label, " + \
                            "ref_count FROM "+TABLE+" WHERE dataset=\'"+dataset+"\' AND label=\'"+label+"\'"
            rows = db_session.execute(cql)
            rows = list(rows)

            if len(rows) == 0:
                # not yet in database
                return cls(dataset, label, RefCountType.LABEL)
            elif len(rows) == 1:
                r = rows[0]
                return cls(dataset, label, RefCountType.LABEL, r.ref_count)
            elif len(rows) > 1:
                app.logger.warning('Query error: the same key cannot appear twice.')
                return None

    @classmethod
    def from_category(cls, dataset, category):
        TABLE = "category_ref_count"
        with app.app_context():
            db_session = database_controller.get_db(app.config)
            cql = "SELECT dataset, " + \
                            "category, " + \
                            "ref_count FROM "+TABLE+" WHERE dataset=\'"+dataset+"\' AND category=\'"+category+"\'"
            rows = db_session.execute(cql)
            rows = list(rows)

            if len(rows) == 0:
                # not yet in database
                return cls(dataset, category, RefCountType.CATEGORY)
            elif len(rows) == 1:
                r = rows[0]
                return cls(dataset, category, RefCountType.CATEGORY, r.ref_count)
            elif len(rows) > 1:
                app.logger.warning('Query error: the same key cannot appear twice.')
                return None

    def upsert(self):
        TABLE, field = RefCountModel.get_table_and_field_from_type(self.type)
        cql = self.db_session.prepare("INSERT INTO "+TABLE+"(dataset, "+field+", ref_count) " + \
                                        "VALUES (?, ?, ?)")
        self.db_session.execute(cql, [self.dataset, self.name, self.ref_count])

    @staticmethod
    def get_table_and_field_from_type(ref_type):
        if ref_type == RefCountType.CATEGORY:
            return "category_ref_count", "category"
        elif ref_type == RefCountType.LABEL:
            return "label_ref_count", "label"    

    @staticmethod
    def get_all(dataset, ref_type):
        TABLE, field = RefCountModel.get_table_and_field_from_type(ref_type)
        with app.app_context():
            db_session = database_controller.get_db(app.config)
            cql = "SELECT "+field+", ref_count FROM "+TABLE+" WHERE dataset=\'"+dataset+"\'"
            rows = db_session.execute(cql)

            values = []
            for r in rows:
                if r.ref_count > 0:
                    if ref_type == RefCountType.CATEGORY:
                        values.append(r.category)
                    elif ref_type == RefCountType.LABEL:
                        values.append(r.label)

            return values

    @staticmethod
    def get_all_labels(dataset):
        return RefCountModel.get_all(dataset, RefCountType.LABEL)

    @staticmethod
    def get_all_categories(dataset):
        return RefCountModel.get_all(dataset, RefCountType.CATEGORY)



