
from annotator_supreme.models.image_model import ImageModel
from annotator_supreme.models.bbox_model import BBox
from annotator_supreme.controllers.base_controller import memoized_ttl
from annotator_supreme.models.dataset_model import DatasetModel
from annotator_supreme.controllers.image_utils import ImageUtils
from annotator_supreme.controllers.ref_count_controller import RefCountController


class ImageController():

    def __init__(self):
        self.ref_controller = RefCountController()

    def create_image(self, dataset_name, image, name = "", bboxes=[], category="", partition = 0, fold = 0):
        try:
            img = ImageModel("", dataset_name, image, name, bboxes, category, partition, fold)
            img.upsert()

            self.ref_controller.increment_category_reference(dataset_name, category)

            # # att the category and labels of the dataset
            # dataset = DatasetModel.from_name(dataset_name)
            # if category not in dataset.image_categories:
            #     dataset.add_image_category(category)

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
            "last_modified": img_o.last_modified,
            "has_annotation": len(img_o.bboxes) > 0
        }

    def get_image_object(self, dataset_name, id):
        """ Returns the metadata stored in database about this image """
        img_o = ImageModel.from_database_and_key(dataset_name, id)
        return img_o

    def get_image(self, dataset_name, id):
        """ Returns the actual image binary file """
        img_o = self.get_image_object(dataset_name, id)
        return img_o.image

    def set_partition(self, dataset_name, id, partition):
        img_o = ImageModel.from_database_and_key(dataset_name, id)
        img_o.partition = partition
        img_o.upsert()

    def change_annotations(self, dataset, id, anno):
        img_o = ImageModel.from_database_and_key(dataset, id)

        # decrement label from old annotation and increment for the new ones
        for an in img_o.bboxes:
            for lbl in an.labels:
                self.ref_controller.decrement_label_reference(dataset, lbl)

        for an in anno:
            for lbl in an.labels:
                self.ref_controller.increment_label_reference(dataset, lbl)
        img_o.change_bboxes(anno)

    def delete_image(self, dataset, image_id):
        img_o = ImageModel.from_database_and_key(dataset, image_id)

        # remove reference for category
        self.ref_controller.decrement_category_reference(dataset, img_o.category)

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


    def set_aspect_ratio_image(self, dataset, image_id, aspect_ratio):
        img_o = ImageModel.from_database_and_key(dataset, image_id)
        if img_o is None:
            return (False, "No able to find image, check you parameters!")

        aspect_ratio = aspect_ratio.lower()
        if aspect_ratio != "4:3":
            return (False, "aspect_ratio must 4:3!")

        (img_o.image, off_x, off_y) = ImageUtils.set_aspect_ratio(img_o.image, aspect_ratio)
        print("off_x", off_x)

        # TODO: these two lines should be on the upsert, no?
        img_o.width = img_o.image.shape[1]
        img_o.height = img_o.image.shape[0]

        new_bboxes = []
        for b in img_o.bboxes:
            bb_obj = BBox(b.top, b.left, b.bottom, b.right, b.labels, b.ignore)
            bb_obj.set_x_offset(-off_x)
            bb_obj.set_y_offset(-off_y)

            new_bboxes.append(bb_obj)

        img_o.bboxes = new_bboxes

        img_o.upsert()

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
