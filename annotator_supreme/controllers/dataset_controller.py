
from annotator_supreme.models.dataset_model import DatasetModel
from annotator_supreme.models.image_model import ImageModel
from annotator_supreme.controllers.image_controller import ImageController
import random


class DatasetController():

    def __init__(self):
        self.image_controller = ImageController()

    def create_dataset(self, dataset_name, tags):
        d = DatasetModel(dataset_name, tags)
        d.upsert()

    def get_dataset(self, dataset_name):
        d = DatasetModel.from_name(dataset_name)
        return d

    def get_datasets(self, dataset_name = ""):
        if dataset_name == "":
            rows = DatasetModel.list_datasets()
            datasets = []
            for ds_row in rows:
                datasets.append({'name': ds_row.name, 
                        'tags': ds_row.tags, 
                        'annotation_labels': ds_row.annotation_labels, 
                        'image_categories': ds_row.image_categories, 
                        'last_modified': ds_row.last_modified})

            return datasets

    def set_partition(self, dataset_name, partitions, percentages):
        """
        This function sets the partition (usually test and training)
        """
        if len(partitions) == 0:
            return (False, "No partition provided!")
        if len(partitions) != len(percentages):
            return (False, "Number of percentages should be equal to the number of partitions.")

        ps = [DatasetController.partition_id(p) for p in partitions]
        if -1 in ps:
            return (False, "Did not recognize some (or all) partitions specified.")
        if sum(percentages) - 1 > 10e-3:
            return (False, "Sum of percentages should be equal to one.")            

        all_images = ImageController.all_images(dataset_name)
        random.shuffle(all_images)

        if len(percentages) > 2:
            return (False, "More than one partition not implemented")

        fold1 = int(len(all_images)*percentages[0])
        for img in all_images[:fold1]:
            self.image_controller.set_partition(dataset_name, img["phash"], ps[0])
        for img in all_images[fold1:]:
            self.image_controller.set_partition(dataset_name, img["phash"], ps[1])

        return (True, "")


    def purge_dataset(self, dataset_name):
        # first delete all iamges/annotations from the dataset
        ok, error = ImageModel.delete_all_images(dataset_name)
        if ok:
            d = DatasetModel(dataset_name)
            ok, error = d.delete()
            return ok, error
        else:
            return ok, error


    @staticmethod
    def partition_id(partition):
        if partition.lower() == "training":
            return 0
        elif partition.lower() == "testing":
            return 1
        else:
            return -1


