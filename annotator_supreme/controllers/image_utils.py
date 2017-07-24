import cv2
import numpy as numpy

class ImageUtils:

    @staticmethod
    def create_thumbnail(image, annotations):
        image = ImageUtils.plot_annotations(image, annotations)
        if image.shape[0] < image.shape[1]:
            factor = 200./image.shape[0]
            # make height 200, and width accordantly
            image = cv2.resize(image, (int(image.shape[1]*factor), 200))
            # get only the center portion of image
            w = image.shape[1]
            return image[:, (w-200)//2:(w+200)//2, :]
        else:
            factor = 200./image.shape[1]
            # make height 200, and width accordantly
            image = cv2.resize(image, (200, int(image.shape[0]*factor)))
            # get only the center portion of image
            h = image.shape[0]
            return image[(h-200)//2:(h+200)//2, :, :]

    @staticmethod
    def plot_annotations(image, annotations):
        for a in annotations.bboxes:
            cv2.rectangle(image, (int(a.left), int(a.top)), (int(a.right), int(a.bottom)), (20, 20, 200), 5)
        return image

    @staticmethod
    def rotate_image(image, orientation):
        if orientation == "ccw":
            img_ccw = cv2.transpose(image)
            return cv2.flip(img_ccw, 0)
        elif orientation == "cw":
            img_cw = cv2.flip(image, 0)
            return cv2.transpose(img_cw)
        else:
            return image


    @staticmethod
    def flip_image(image, direction):
        if direction == "h":
            return cv2.flip(image, 1)
        elif direction == "v":
            return cv2.flip(image, 0)
        else:
            return image
