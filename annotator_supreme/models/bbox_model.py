

# create a class to map to the "bbox" type in Cassandra
class BBox:

    def __init__(self, top, left, bottom, right, labels, ignore = False):
        self.top = top
        self.left = left
        self.bottom = bottom
        self.right = right
        self.labels = labels
        self.ignore = ignore
