from annotator_supreme.models.ref_count_model import RefCountModel

class RefCountController:

    def __init__(self):
        pass

    def increment_label_reference(self, dataset, label):
        ref = RefCountModel.from_label(dataset, label)
        ref.ref_count = ref.ref_count + 1
        ref.upsert()

    def decrement_label_reference(self, dataset, label):
        ref = RefCountModel.from_label(dataset, label)
        ref.ref_count = ref.ref_count - 1
        ref.upsert()

    def get_all_labels(self, dataset):
        return RefCountModel.get_all_labels(dataset)

    def increment_category_reference(self, dataset, category):
        ref = RefCountModel.from_category(dataset, category)
        ref.ref_count = ref.ref_count + 1
        ref.upsert()

    def decrement_category_reference(self, dataset, category):
        ref = RefCountModel.from_category(dataset, category)
        ref.ref_count = ref.ref_count - 1
        ref.upsert()

    def get_all_categories(self, dataset):
        return RefCountModel.get_all_categories(dataset)