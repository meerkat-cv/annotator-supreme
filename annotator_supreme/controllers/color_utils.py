
import cv2
import numpy as np

class ColorUtils:

    # this is a list of 26 distinguishable colors suggested by Paul Green-Armytage
    # for white background, taken from https://graphicdesign.stackexchange.com/questions/3682/where-can-i-find-a-large-palette-set-of-contrasting-colors-for-coloring-many-d
    PGA_colors = [(240,163,255),
                    (0,117,220),
                    (153,63,0),
                    (76,0,92),
                    (25,25,25),
                    (0,92,49),
                    (43,206,72),
                    (255,204,153),
                    (128,128,128),
                    (148,255,181),
                    (143,124,0),
                    (157,204,0),
                    (194,0,136),
                    (0,51,128),
                    (255,164,5),
                    (255,168,187),
                    (66,102,0),
                    (255,0,16),
                    (94,241,242),
                    (0,153,143),
                    (224,255,102),
                    (116,10,255),
                    (153,0,0),
                    (255,255,128),
                    (255,255,0),
                    (255,80,5)]

    @staticmethod
    def distiguishable_colors(n_colors):
        return PGA_colors[:n_colors]

    @staticmethod
    def distiguishable_colors_hex(n_colors):
        return [rgb2hex(c) for c in PGA_colors[:n_colors]]

    @staticmethod
    def rgb2hex(rgb):
        """
        rgb must be a 3-tuple as the colors above
        """
        return '#%02x%02x%02x' % rgb
