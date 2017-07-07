import cv2
import numpy as np

_VERSION = '0.0.1'

def process(im, anno):
    im_blur = im

    if anno is not None:
        for bb in anno['anno']:
            if not bb['ignore']:
                continue
            (l,t,r,b) = (int(bb['left']), int(bb['top']), int(bb['right']), int(bb['bottom']))
            (l,t,r,b) = fix_bb(l,t,r,b,im.shape)

            if (r-l)*(b-t) <= 0:
                continue

            biggest_dim = r-l
            if (b-t) > biggest_dim:
                biggest_dim = b-t
            kernel_size = int(biggest_dim/5.0) + (1-int(biggest_dim/5.0)%2)
            im_blur[t:b,l:r] = cv2.GaussianBlur(im_blur[t:b,l:r], (kernel_size, kernel_size), biggest_dim/5.0)

    return (im_blur, anno)


def init():
    pass

def end():
    pass

def get_parameters():
    return {'parameters': []}

def get_version():
    return _VERSION

def fix_bb(l, t, r, b, shape):
    if l<0: l=0
    if t<0: t=0
    if b>=shape[0]: b=shape[0]-1
    if r>=shape[1]: r=shape[1]-1

    return (l,t,r,b)
