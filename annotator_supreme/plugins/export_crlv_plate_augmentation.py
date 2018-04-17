import imgaug as ia
from imgaug import augmenters as iaa
import os
import cv2
import numpy as np


DATASET_DIR = '/media/meerkat/Data/datasets/docs_crlv_plate_augmented'
NUM_AUG_IMAGES = 10
NUM_SCALES = 3
MAX_SCALE = 1.6
IM_HEIGHT = 64
alphabet = '0123456789abcdefghijklmnopqrstuvwxyz/'




# Sometimes(0.5, ...) applies the given augmenter in 50% of all cases,
# e.g. Sometimes(0.5, GaussianBlur(0.3)) would blur roughly every second image.
sometimes = lambda aug: iaa.Sometimes(0.5, aug)

# execute 0 to 5 of the following (less important) augmenters per image
# don't execute all of them, as that would often be way too strong
im_filters = iaa.SomeOf((0, 5),
    [
        iaa.OneOf([
            iaa.GaussianBlur((0, 1.5)), # blur images with a sigma between 0 and 3.0
            iaa.AverageBlur(k=(2, 5)), # blur image using local means with kernel sizes between 2 and 7
            iaa.MedianBlur(k=(3, 7)), # blur image using local medians with kernel sizes between 2 and 7
        ]),
        iaa.Sharpen(alpha=(0, 0.1), lightness=(0.75, 1.5)), # sharpen images
        iaa.AdditiveGaussianNoise(loc=0, scale=(0.0, 0.05*255), per_channel=0.5), # add gaussian noise to images
        iaa.Multiply((0.5, 1.5), per_channel=0.5), # change brightness of images (50-150% of original value)
        iaa.Add((-20, 20)), # change brightness of images (by -10 to 10 of original value)
        iaa.OneOf([
            iaa.ContrastNormalization((0.75, 1.75), per_channel=0.5), # improve or worsen the contrast
            iaa.ContrastNormalization((0.5, 1.5)), # improve or worsen the contrast
        ]),
        iaa.Grayscale(alpha=(0.0, 1.0)),
    ],
    random_order=True
)

# Define our sequence of augmentation steps that will be applied to every image
# All augmenters with per_channel=0.5 will sample one value _per image_
# in 50% of all cases. In all other cases they will sample new values
# _per channel_.
seq_3 = iaa.Sequential(
    [
        # apply the following augmenters to most images
        sometimes(iaa.Crop(percent=(0, 0.1))), # crop images by 0-10% of their height/width
        sometimes(iaa.Affine(
            scale={"x": (0.8, 1.2), "y": (0.8, 1.2)}, # scale images to 80-120% of their size, individually per axis
            translate_percent={"x": (-0.05, 0.05), "y": (-0.05, 0.05)}, # translate by -20 to +20 percent (per axis)
            rotate=(-4, 4), # rotate by -45 to +45 degrees
            shear=(-6, 6), # shear by -16 to +16 degrees
            order=[0, 1], # use nearest neighbour or bilinear interpolation (fast)
            cval=(0, 255), # if mode is constant, use a cval between 0 and 255
            mode='edge' # use any of scikit-image's warping modes (see 2nd image from the top for examples)
        )),
        im_filters
    ],
    random_order=True
)

seq_2 = iaa.Sequential(
    [
        # apply the following augmenters to most images
        sometimes(iaa.Crop(percent=(0, 0.05))), # crop images by 0-10% of their height/width
        sometimes(iaa.Affine(
            scale={"x": (0.9, 1.1), "y": (0.9, 1.1)}, # scale images to 80-120% of their size, individually per axis
            translate_percent={"x": (-0.05, 0.05), "y": (-0.05, 0.05)}, # translate by -20 to +20 percent (per axis)
            rotate=(-3, 3), # rotate by -45 to +45 degrees
            shear=(-6, 6), # shear by -16 to +16 degrees
            order=[0, 1], # use nearest neighbour or bilinear interpolation (fast)
            cval=(0, 255), # if mode is constant, use a cval between 0 and 255
            mode='edge' # use any of scikit-image's warping modes (see 2nd image from the top for examples)
        )),
        im_filters
    ],
    random_order=True
)

seq_1 = iaa.Sequential(
    [
        sometimes(iaa.Affine(
            scale={"x": (0.95, 1.05), "y": (0.95, 1.05)}, # scale images to 80-120% of their size, individually per axis
            translate_percent={"x": (-0.025, 0.025), "y": (-0.05, 0.025)}, # translate by -20 to +20 percent (per axis)
            rotate=(0, 0), # rotate by -45 to +45 degrees
            shear=(-6, 6), # shear by -16 to +16 degrees
            order=[0, 1], # use nearest neighbour or bilinear interpolation (fast)
            cval=(0, 255), # if mode is constant, use a cval between 0 and 255
            mode='edge' # use any of scikit-image's warping modes (see 2nd image from the top for examples)
        )),
        im_filters
    ],
    random_order=True
)



class AnnotatorPlugin:
    _VERSION = '0.0.1'

    def __init__(self, dataset, partition, additional_params = {}):
        self.image_path_list = [[],[]]
        self.label_list = [[],[]]
        try:
            os.system('rm -rf '+DATASET_DIR)
        except:
            pass
        os.system('mkdir '+DATASET_DIR)
        os.system('mkdir '+DATASET_DIR+'/train/')
        os.system('mkdir '+DATASET_DIR+'/val/')


    def is_date(self, text):
        return len(text.split('/')) == 3

    def process(self, im, anno):
        part = anno['partition']
        print('partition', part)
        if part == 0:
            im_name = DATASET_DIR+'/train/'+anno['phash']
        else:
            im_name = DATASET_DIR+'/val/'+anno['phash']
        width   = float(im.shape[1])
        height  = float(im.shape[0])
        curr_tag = ''
        # print('processing', anno['phash'])

        annotations = []
        imgs_vec    = []
        txt_vec     = []
        curr_im = 0
        for bb in anno['anno']:
            if bb['ignore']:
                continue

            if len(bb['labels']) <= 0:
                continue

            if bb['labels'][0] != 'plate' and bb['labels'][0] != 'plate1' and bb['labels'][0] != 'plate2' and bb['labels'][0] != 'plate_ant':
                continue

            curr_label = ''
            if len(bb['labels']) > 1:
                curr_label = bb['labels'][1].lower()
            curr_label = curr_label.replace(' ','')
            bad_letter = False
            for a in curr_label:
                if a not in alphabet:
                    print('invalid char', a, anno['phash'])
                    bad_letter = True
                    
            if bad_letter:
                continue
                    
            # curr_label = curr_label.replace('-','')
            # curr_label = curr_label.replace('.','')

            l = int(bb['left'])
            t = int(bb['top'])
            r = int(bb['right'])
            b = int(bb['bottom'])

            for i in range(0,NUM_SCALES):
                curr_scale = 1+(MAX_SCALE-1)/NUM_SCALES*(i+1)
                (nl, nt, nr, nb) = self.safe_scale_bbox(l, t, r, b, curr_scale, im.shape)
                # imgs_vec = np.asarray([np.copy(im[nt:nb,nl:nr,:])])
                aux_im = np.copy(im[nt:nb,nl:nr,:])
                if aux_im.shape[0] <= 0 or aux_im.shape[1] <= 0:
                    break
                scale_im = IM_HEIGHT/float(aux_im.shape[0])
                aux_im = cv2.resize(aux_im, (int(aux_im.shape[1]*scale_im), IM_HEIGHT))
                imgs_vec = np.asarray([aux_im])
                txt_vec.append(curr_label)

                for aug in range(0,NUM_AUG_IMAGES):
                    if curr_scale <= 1.2:
                        images_aug = seq_1.augment_images(imgs_vec)
                    elif curr_scale < 1.6:
                        images_aug = seq_2.augment_images(imgs_vec)
                    else:
                        images_aug = seq_3.augment_images(imgs_vec)

                    for j in range(0,len(images_aug)):
                        curr_name = im_name+'_'+str(curr_im).zfill(4)
                        with open(curr_name+'.txt', 'w') as f:
                            f.write(curr_label+'\n')
                        cv2.imwrite(curr_name+'.png', images_aug[j,:])
                        self.image_path_list[part].append(curr_name+'.png')
                        self.label_list[part].append(curr_label)
                        curr_im += 1



        return (im, anno)


    def end(self):
        with open(DATASET_DIR+'/train/image_path_list.txt', 'w') as f:
            for p in self.image_path_list[0]:
                f.write(p+'\n')

        with open(DATASET_DIR+'/train/label_list.txt', 'w') as f:
            for l in self.label_list[0]:
                f.write(l+'\n')

        with open(DATASET_DIR+'/val/image_path_list.txt', 'w') as f:
            for p in self.image_path_list[1]:
                f.write(p+'\n')

        with open(DATASET_DIR+'/val/label_list.txt', 'w') as f:
            for l in self.label_list[1]:
                f.write(l+'\n')

    def get_parameters(self):
        return {'parameters': []}

    def get_version(self):
        return self._VERSION

    def safe_scale_bbox(self, l, t, r, b, scale, shape):
        dw = (r-l)*(scale-1)/6.0
        dh = (b-t)*(scale-1)/2.0

        l = int(l-dw)
        t = int(t-dh)
        r = int(r+dw)
        b = int(b+dh)

        if l<0: l=0
        if t<0: t=0
        if b>=shape[0]: b=shape[0]-1
        if r>=shape[1]: r=shape[1]-1

        return (l,t,r,b)
