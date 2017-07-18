
from annotator_supreme.models.dataset_model import DatasetModel
from annotator_supreme.models.image_model import ImageModel


class DatasetController():

    def __init__(self):
        pass

    def create_dataset(self, dataset_name, tags):
        d = DatasetModel(dataset_name, tags)
        d.upsert()

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

    def purge_dataset(self, dataset_name):
        # first delete all iamges/annotations from the dataset
        ok, error = ImageModel.delete_all_images(dataset_name)
        if ok:
            d = DatasetModel(dataset_name)
            ok, error = d.delete()
            return ok, error
        else:
            return ok, error


