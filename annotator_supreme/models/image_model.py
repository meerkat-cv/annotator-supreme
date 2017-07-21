from annotator_supreme import app
from annotator_supreme.controllers import database_controller
from annotator_supreme.models.bbox_model import BBox
from PIL import Image
import hashlib
import imagehash
import time
import cv2
import numpy as np
import datetime

TABLE = "images"

class Dummy:

    def __init__(self, labels):
        self.labels = "hehe"

class ImageModel():

    def __init__(self, phash, dataset_name, image, name = "", bboxes=[], category="", partition = 0, fold = 0, last_modified = None):

        if dataset_name is None or dataset_name == "":
            raise Exception("An image needs needs a dataset name.")

        self.dataset_name = dataset_name
        self.name = name
        if image is None or image.shape[0] == 0:
            raise Exception("An image needs an image.")

        self.width = image.shape[1];
        self.height = image.shape[0];
        self.image = image

        if phash == "":
            # given the image, we compute the percepetual hash to use as key
            self.phash = self.compute_phash(image)
        else:
            self.phash = phash
        self.bboxes = bboxes

        if category == "":
            self.category = "default"
        else:
            self.category = category

        self.partition = partition
        self.fold = fold
        self.last_modified = last_modified

        with app.app_context():
            self.db_session = database_controller.get_db(app.config)

    @classmethod
    def from_database_and_key(cls, dataset, image_key):
        with app.app_context():
            db_session = database_controller.get_db(app.config)
            cql = "SELECT phash, "+ \
                        "dataset, " + \
                        "img, " + \
                        "width, " + \
                        "height, " + \
                        "name, " + \
                        "annotation, "+ \
                        "category, " + \
                        "partition, " + \
                        "fold, " + \
                        "last_modified FROM "+TABLE+" WHERE dataset=\'"+dataset+"\' AND phash=\'"+image_key+"\'"
            rows = db_session.execute(cql)
            rows = list(rows)


            if len(rows) == 0:
                app.logger.warning('Did not found doc with the provided dataset and ID.')
                return None
            elif len(rows) == 1:
                r = rows[0]
                image = np.fromstring(r.img, dtype=np.uint8)
                image = cv2.imdecode(image, cv2.IMREAD_COLOR)
                image = image.reshape(r.height, r.width, 3)

                return cls(r.phash, r.dataset, image, r.name, r.annotation, r.category, r.partition, r.fold, r.last_modified)
            elif len(rows) > 1:
                app.logger.warning('Query error: the same image cannot appear twice.')
                return None



    def add_bbox(self, top, left, bottom, right, labels, ignore = False, update_db = False):
        b = BBox(top, left, bottom, right, labels, ignore)
        self.bboxes.append(b)

        if update_db:
            self.upsert()

    def change_bboxes(self, bboxes):
        self.bboxes = bboxes
        self.upsert()

    def upsert(self):
        # TODO: transform to update to really do upsert
        cql = self.db_session.prepare(" INSERT INTO "+TABLE+ \
                                    " (phash, "+ \
                                    "dataset, " + \
                                    "img, " + \
                                    "width, " + \
                                    "height, " + \
                                    "name, " + \
                                    "annotation, " + \
                                    "category, " + \
                                    "partition, " + \
                                    "fold, " + \
                                    "last_modified) " + \
                                    " VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?) ")

        image = cv2.imencode('.png', self.image)[1]
        self.db_session.execute(cql, [self.phash, \
                                        self.dataset_name, \
                                        image.tostring(), \
                                        self.width, \
                                        self.height, \
                                        self.name, \
                                        self.bboxes, \
                                        self.category, \
                                        self.partition, \
                                        self.fold, \
                                        datetime.datetime.now() ] )

    def compute_phash(self, image):
        # pil_image = Image.fromarray(image)
        # return str(imagehash.phash(pil_image))
        m = hashlib.md5()
        m.update(image)
        return m.hexdigest()


    @staticmethod
    def list_images_from_dataset(dataset_name):
        with app.app_context():
            db_session = database_controller.get_db(app.config)
            cql = "SELECT phash, "+ \
                        "width, " + \
                        "height, " + \
                        "name, " + \
                        "annotation, "+ \
                        "category, " + \
                        "partition, " + \
                        "fold, " + \
                        "last_modified FROM "+TABLE+" WHERE dataset=\'"+dataset_name+"\'"
            rows = db_session.execute(cql, timeout=60)
            imgs = list(rows)

            return imgs

    @staticmethod
    def delete_image(dataset_name, image_id):
        with app.app_context():
            db_session = database_controller.get_db(app.config)

            cql = "DELETE FROM "+TABLE+" WHERE dataset=\'"+dataset_name+"\'" + " AND phash=\'" + image_id +"\'"
            res = db_session.execute(cql)

            return (True, "")

    @staticmethod
    def delete_all_images(dataset_name):
        with app.app_context():
            db_session = database_controller.get_db(app.config)

            cql = "DELETE FROM "+TABLE+" WHERE dataset=\'"+dataset_name+"\'"
            res = db_session.execute(cql)

            return (True, "")
