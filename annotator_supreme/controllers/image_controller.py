
from annotator_supreme.models.image_model import ImageModel


class ImageController():

    def __init__(self):
        pass

    def create_image(self, dataset_name, image, name = "", bboxes=[], category="", partition = 0, fold = 0): 
        i = ImageModel(dataset_name, image, name, bboxes, category, partition, fold)
        i.upsert()

    def all_images(self, dataset_name):
        all_images = ImageModel.list_images_from_dataset(dataset_name)
        return all_images

    