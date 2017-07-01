
from annotator_supreme.models.image_model import ImageModel


class ImageController():

    def __init__(self):
        pass

    def create_image(self, dataset_name, image, name = "", bboxes=[], category="", partition = 0, fold = 0): 
        try:
            img = ImageModel("", dataset_name, image, name, bboxes, category, partition, fold)
            img.upsert()
            return (True, "", img.phash)
        except:
            return (False, "Unexpected error while adding in database.", None)

    def get_image(self, dataset_name, id):
        img_o = ImageModel.from_database_and_key(dataset_name, id)
        return img_o.image

    def all_images(self, dataset_name):
        all_images = ImageModel.list_images_from_dataset(dataset_name)
        return all_images

    