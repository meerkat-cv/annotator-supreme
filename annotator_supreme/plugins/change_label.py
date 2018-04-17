import os
import cv2
import numpy as np
import copy

class AnnotatorPlugin:
    _VERSION = '0.0.1'

    def __init__(self, dataset, partition = None, additional_params = {}):
        self.new_labels = additional_params['new_labels']
        

    def process(self, image_matrix, image_object):
        new_image_object = copy.copy(image_object)
        for i,an in enumerate(new_image_object['anno']):
            if 'labels' in an:
                new_image_object['anno'][i]['labels'] = self.new_labels

        return (image_matrix, new_image_object)

    def end(self):
        pass

    def get_parameters(self):
        return {'parameters': []}

    def get_version(self):
        return _VERSION


