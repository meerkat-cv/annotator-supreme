
from annotator_supreme.models.image_model import ImageModel
from annotator_supreme.controllers.base_controller import memoized_ttl
from annotator_supreme.models.dataset_model import DatasetModel
from annotator_supreme.controllers.image_utils import ImageUtils


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

        except BaseException as e:
            return (False, "Unexpected error while adding in database: "+str(e), None)

    def get_image_details(self, dataset_name, id):
        img_o = ImageModel.from_database_and_key(dataset_name, id)
        return {
            "id": img_o.phash,
            "dataset": img_o.dataset_name,
            "name": img_o.name,
            "width": img_o.width,
            "height": img_o.height,
            "category": img_o.category,
            "partition": img_o.partition,
            "fold": img_o.fold,
            "last_modified": img_o.last_modified
        }


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

    def rotate_image(self, dataset, image_id, orientation):
        img_o = ImageModel.from_database_and_key(dataset, image_id)
        if img_o is None:
            return (False, "No able to find image, check you parameters!")

        orientation = orientation.lower()
        if orientation != "cw" and orientation != "ccw":
            return (False, "Orientation must be cw or ccw!")

        img_o.image = ImageUtils.rotate_image(img_o.image, orientation)
        aux = img_o.width
        img_o.width = img_o.height
        img_o.height = aux
        img_o.upsert();

        return (True, "")

    def flip_image(self, dataset, image_id, direction):
        img_o = ImageModel.from_database_and_key(dataset, image_id)
        if img_o is None:
            return (False, "No able to find image, check you parameters!")

        direction = direction.lower()
        if direction != "h" and direction != "v":
            return (False, "Direction must be h or v!")

        img_o.image = ImageUtils.flip_image(img_o.image, direction)
        img_o.upsert();

        return (True, "")

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
