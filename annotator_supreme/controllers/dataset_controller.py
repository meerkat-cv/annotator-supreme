
from annotator_supreme.models.dataset_model import DatasetModel


class DatasetController():

    def __init__(self):
        pass

    def create_dataset(self, dataset_name, tags):
        d = DatasetModel(dataset_name, tags)
        d.upsert()

    def get_datasets(self, dataset_name = ""):
        if dataset_name == "":
            rows = DatasetModel.list_datasets()
            print("rows", rows)
            datasets = []
            for ds_row in rows:
                print('ds_row', ds_row.name)
                print('ds_row', ds_row.tags)
                datasets.append({'name': ds_row.name, 'tags': ds_row.tags})

            print("datasets:", datasets)
            return datasets