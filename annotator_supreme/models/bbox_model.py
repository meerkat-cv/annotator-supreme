

# create a class to map to the "bbox" type in Cassandra
class BBox:

    def __init__(self, top, left, bottom, right, labels, ignore = False):
        self.top = top
        self.left = left
        self.bottom = bottom
        self.right = right
        self.labels = labels
        self.ignore = ignore

    def scale_itself(self, scale_factor):
        self.top = self.top*scale_factor
        self.left = self.left*scale_factor
        self.bottom = self.bottom*scale_factor
        self.right = self.right*scale_factor


    def set_x_offset(self, x_offset):
        self.left = self.left+x_offset
        self.right = self.right+x_offset

    def set_y_offset(self, y_offset):
        self.top = self.top+y_offset
        self.bottom = self.bottom+y_offset