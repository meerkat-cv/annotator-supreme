from annotator_supreme import app
from annotator_supreme.controllers import database_controller
from annotator_supreme.models.bbox_model import BBox
from PIL import Image
import imagehash
import time

TABLE = "images"

class Dummy:

    def __init__(self, labels):
        self.labels = "hehe"

class ImageModel():

    def __init__(self, dataset_name, image, name = "", bboxes=[], category="", partition = 0, fold = 0):
        
        if dataset_name is None or dataset_name == "":
            raise Exception("An image needs needs a dataset name.")

        self.dataset_name = dataset_name
        self.name = name
        if image is None or image.shape[0] == 0:
            raise Exception("An image needs an image.")
        self.image = image
        # given the image, we compute the percepetual hash to use as key
        self.phash = self.compute_phash(image)
        self.bboxes = bboxes
        self.category = "defaul"
        self.partition = partition
        self.fold = fold

        with app.app_context():
            self.db_session = database_controller.get_db(app.config)

    def add_bbox(self, top, left, bottom, right, labels, ignore = False, update_db = False):
        b = BBox(top, left, bottom, right, labels, ignore)
        self.bboxes.append(b)

        if update_db:
            self.upsert()

    def upsert(self):
        # TODO: transform to update to really do upsert
        cql = self.db_session.prepare(" INSERT INTO "+TABLE+" (phash, "+ \
                                    "dataset, " + \
                                    "name, " + \
                                    "img, " + \
                                    "category, " + \
                                    "partition, " + \
                                    "fold, " + \
                                    "last_modified, " + \
                                    "annotation) " + \
                                    " VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?) ")
              
        print("query to include image there ",cql)
        d = [BBox(0,0,0,0, ["aaa", "bbb"]), BBox(30,30,30,30, ["ccc", "ddd"])]
        self.db_session.execute(cql, [self.phash, \
                                        self.dataset_name, \
                                        self.name, \
                                        self.image.tobytes(), \
                                        self.category, \
                                        self.partition, \
                                        self.fold, \
                                        int(time.time()), \
                                        d])

    def compute_phash(self, image):
        pil_image = Image.fromarray(image)
        return str(imagehash.phash(pil_image))


    @staticmethod
    def list_images_from_dataset(dataset_name):
        with app.app_context():
            db_session = database_controller.get_db(app.config)
            rows = db_session.execute('SELECT phash FROM '+TABLE)
            return list(rows)