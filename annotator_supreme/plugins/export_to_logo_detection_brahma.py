import os
import cv2
import numpy as np

_VERSION = '0.0.1'
DATASET_DIR = '/media/meerkat/Data/datasets/logo_detection_brahma'
tags = [ 'Brahma']
images_list = []

def process(im, anno):
    im_name = DATASET_DIR+'/'+anno['phash']
    width   = float(im.shape[1])
    height  = float(im.shape[0])
    curr_tag = ''

    print('processing', anno['phash'])
    (im, anno) = blur_img(im, anno)

    annotations = []
    for bb in anno['anno']:
        if bb['ignore']:
            continue
        x = ((bb['left']+bb['right'])/2.0) / width
        y = ((bb['top']+bb['bottom'])/2.0) / height
        w = (bb['right']-bb['left']) / width
        h = (bb['bottom']-bb['top']) / height
        curr_tag = bb['labels'][0]
        curr_anno = curr_tag+' '+str(x)+' '+str(y)+' '+str(w)+' '+str(h)
        annotations.append(curr_anno)

    if curr_tag == '':
        curr_tag = 'Distractors'
    with open(DATASET_DIR+'/'+curr_tag+'/'+anno['phash']+'.txt', 'w') as f:
        for a in annotations:
            f.write(a+'\n')

    cv2.imwrite(DATASET_DIR+'/'+curr_tag+'/'+anno['phash']+'.png', im)
    images_list.append(DATASET_DIR+'/'+curr_tag+'/'+anno['phash']+'.png')

    return (im, anno)


def init():
    images_list = []
    try:
        os.system('rm -rf '+DATASET_DIR)
    except:
        pass
    os.system('mkdir '+DATASET_DIR)
    for t in tags:
        os.system('mkdir '+DATASET_DIR+'/'+t)
    os.system('mkdir '+DATASET_DIR+'/Distractors')

def end():
    with open(DATASET_DIR+'/train.txt', 'w') as f:
        for im in images_list:
            f.write(im+'\n')

def get_parameters():
    return {'parameters': []}

def get_version():
    return _VERSION

def blur_img(im, anno):
    im_blur = im

    new_anno = []
    if anno is not None:
        for bb in anno['anno']:
            if not bb['ignore'] and bb['labels'][0] != 'ignore':
                new_anno.append(bb)
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


        anno['anno'] = new_anno

    return (im_blur, anno)

def fix_bb(l, t, r, b, shape):
    if l<0: l=0
    if t<0: t=0
    if b>=shape[0]: b=shape[0]-1
    if r>=shape[1]: r=shape[1]-1

    return (l,t,r,b)
