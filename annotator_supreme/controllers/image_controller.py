
from annotator_supreme.models.image_model import ImageModel
from annotator_supreme.controllers.base_controller import memoized_ttl


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

    @staticmethod
    @memoized_ttl(60)
    def all_images(dataset_name):
        all_images = ImageModel.list_images_from_dataset(dataset_name)

        obj_images = []
        for i in all_images:
            o = {
                "phash": i.phash,
                "url": dataset_name+"/"+i.phash,
                "width": i.width,
                "height": i.height,
                "name": i.name,
                "annotation": i.annotation,
                "category": i.category,
                "partition": i.partition,
                "fold": i.fold,
                "last_modified": i.last_modified
            }
            obj_images.append(o)
        return obj_images
