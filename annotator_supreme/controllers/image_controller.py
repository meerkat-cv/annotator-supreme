
from annotator_supreme.models.image_model import ImageModel
from annotator_supreme.controllers.base_controller import memoized_ttl
from annotator_supreme.models.dataset_model import DatasetModel


class ImageController():

    def __init__(self):
        pass

    def create_image(self, dataset_name, image, name = "", bboxes=[], category="", partition = 0, fold = 0):
        try:
            img = ImageModel("", dataset_name, image, name, bboxes, category, partition, fold)
            img.upsert()
            
            # att the category and labels of the dataset
            dataset = DatasetModel.from_name(dataset_name)
            if category not in dataset.image_categories:
                dataset.add_image_category(category)

            return (True, "", img.phash)

        except:
            return (False, "Unexpected error while adding in database.", None)

    def get_image(self, dataset_name, id):
        img_o = ImageModel.from_database_and_key(dataset_name, id)
        return img_o.image

    def get_image_anno(self, dataset_name, id):
        img_o = ImageModel.from_database_and_key(dataset_name, id)
        return img_o

    def change_annotations(self, dataset, id, anno):
        img_o = ImageModel.from_database_and_key(dataset, id)
        img_o.change_bboxes(anno)

    def delete_image(self, dataset, image_id):
        (ok, error) = ImageModel.delete_image(dataset, image_id)
        return (ok, error)

    @staticmethod
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
