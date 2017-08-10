from annotator_supreme import app
from annotator_supreme.controllers import database_controller
from annotator_supreme.controllers import debug_utils
from annotator_supreme.models.bbox_model import BBox
from PIL import Image
import hashlib
import imagehash
import time
import cv2
import numpy as np
import datetime

TABLE_IMAGES = "images"
TABLE_IMAGES_IMG = "images_img"


with app.app_context():
    db_session = database_controller.get_db(app.config)

upsert_image_cql = db_session.prepare(" INSERT INTO "+TABLE_IMAGES+ \
                                                " (phash, "+ \
                                                "dataset, " + \
                                                "width, " + \
                                                "height, " + \
                                                "name, " + \
                                                "annotation, " + \
                                                "category, " + \
                                                "partition, " + \
                                                "fold, " + \
                                                "last_modified) " + \
                                                " VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?) ")

upsert_image_img_cql = db_session.prepare(" INSERT INTO "+TABLE_IMAGES_IMG+ \
                                                " (phash, img) " + \
                                                " VALUES (?, ?) ")


select_image_cql = db_session.prepare("SELECT phash, "+ \
                                            "dataset, " + \
                                            "width, " + \
                                            "height, " + \
                                            "name, " + \
                                            "annotation, "+ \
                                            "category, " + \
                                            "partition, " + \
                                            "fold, " + \
                                            "last_modified FROM "+TABLE_IMAGES+" WHERE dataset=? AND phash=?")

select_image_img_cql = db_session.prepare("SELECT img FROM "+TABLE_IMAGES_IMG+" WHERE phash=?")



select_image_from_dataset_cql = db_session.prepare("SELECT phash, "+ \
                                                        "width, " + \
                                                        "height, " + \
                                                        "name, " + \
                                                        "annotation, "+ \
                                                        "category, " + \
                                                        "partition, " + \
                                                        "fold, " + \
                                                        "last_modified FROM "+TABLE_IMAGES+" WHERE dataset=?")


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
            db_session = database_controller.get_db(app.config)


    @classmethod
    def from_database_and_key(cls, dataset, image_key):
        debug_utils.DebugUtils.tic()
        with app.app_context():
            db_session = database_controller.get_db(app.config)
            rows = db_session.execute(select_image_cql, [dataset, image_key])
            rows = list(rows)
            
            if len(rows) == 0:
                app.logger.warning('Did not found doc with the provided dataset and ID.')
                return None
            elif len(rows) == 1:
                r = rows[0]

                # get image now
                r_img = db_session.execute(select_image_img_cql, [image_key])
                r_img = list(r_img)

                image = np.fromstring(r_img[0].img, dtype=np.uint8)
                image = cv2.imdecode(image, cv2.IMREAD_COLOR)

                debug_utils.DebugUtils.toc("from_database_and_key")
                
                # image = image.reshape(r.height, r.width, 3)

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
        debug_utils.DebugUtils.tic()
        db_session.execute(upsert_image_cql, [self.phash, \
                                        self.dataset_name, \
                                        self.width, \
                                        self.height, \
                                        self.name, \
                                        self.bboxes, \
                                        self.category, \
                                        self.partition, \
                                        self.fold, \
                                        datetime.datetime.now() ] )

        # also add the image in a different table
        image = cv2.imencode('.png', self.image)[1]
        db_session.execute(upsert_image_img_cql, [self.phash, image.tostring()])
        debug_utils.DebugUtils.toc("image_model.upsert")


    def compute_phash(self, image):
        # pil_image = Image.fromarray(image)
        # return str(imagehash.phash(pil_image))
        m = hashlib.md5()
        m.update(image)
        return m.hexdigest()


    @staticmethod
    def list_images_from_dataset(dataset_name):
        debug_utils.DebugUtils.tic()
        
        with app.app_context():
            db_session = database_controller.get_db(app.config)

            # cql = "SELECT phash, "+ \
            #             "width, " + \
            #             "height, " + \
            #             "name, " + \
            #             "annotation, "+ \
            #             "category, " + \
            #             "partition, " + \
            #             "fold, " + \
            #             "last_modified FROM "+TABLE_IMAGES+" WHERE dataset=\'"+dataset_name+"\'"
            rows = db_session.execute(select_image_from_dataset_cql, [dataset_name], timeout=100)
            imgs = list(rows)

            debug_utils.DebugUtils.toc("list_images_from_dataset ({})".format(dataset_name))
            return imgs

    @staticmethod
    def list_images_phash_from_dataset(dataset_name):
        with app.app_context():
            db_session = database_controller.get_db(app.config)
            cql = "SELECT phash FROM "+TABLE_IMAGES+" WHERE dataset=\'"+dataset_name+"\'"
            rows = db_session.execute(cql, timeout=60)
            imgs = list(rows)

            return imgs

    @staticmethod
    def delete_image(dataset_name, image_id):
        with app.app_context():
            db_session = database_controller.get_db(app.config)

            cql = "DELETE FROM "+TABLE_IMAGES_IMG+" WHERE phash=\'" + image_id +"\'"
            res = db_session.execute(cql)
    

            cql = "DELETE FROM "+TABLE_IMAGES+" WHERE dataset=\'"+dataset_name+"\'" + " AND phash=\'" + image_id +"\'"
            res = db_session.execute(cql)

            
            return (True, "")

    @staticmethod
    def delete_all_images(dataset_name):
        with app.app_context():
            db_session = database_controller.get_db(app.config)

            # first, remove all imgs from images_img table
            phashs = ImageModel.list_images_phash_from_dataset(dataset_name)
            
            for p in phashs:
                cql = "DELETE FROM "+TABLE_IMAGES_IMG+" WHERE phash=\'" + p.phash +"\'"
                res = db_session.execute(cql)

            cql = "DELETE FROM "+TABLE_IMAGES+" WHERE dataset=\'"+dataset_name+"\'"
            res = db_session.execute(cql)

            return (True, "")
