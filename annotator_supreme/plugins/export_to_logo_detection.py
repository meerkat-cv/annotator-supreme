import os
import cv2
import numpy as np

class AnnotatorPlugin:
    _VERSION = '0.0.1'

    def __init__(self, dataset):
        self.dataset_dir = '/tmp/logo_detection_' + dataset["name"]
        self.tags = dataset["annotation_labels"]
        self.images_list = []

        try:
            os.system('rm -rf ' + self.dataset_dir)
        except:
            pass
        os.system('mkdir ' + self.dataset_dir)

        
        for t in self.tags:
            os.system('mkdir ' + self.dataset_dir+'/'+t)
        os.system('mkdir ' + self.dataset_dir + '/Distractors')


    def process(self, im, anno):
        im_name = self.dataset_dir + '/' + anno['phash']
        width   = float(im.shape[1])
        height  = float(im.shape[0])
        curr_tag = ''

        print('processing', anno['phash'])
        (im, anno) = self.blur_img(im, anno)

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
        with open(self.dataset_dir+'/'+curr_tag+'/'+anno['phash']+'.txt', 'w') as f:
            for a in annotations:
                f.write(a+'\n')

        cv2.imwrite(self.dataset_dir+'/'+curr_tag+'/'+anno['phash']+'.png', im)
        self.images_list.append(self.dataset_dir+'/'+curr_tag+'/'+anno['phash']+'.png')

        return (im, anno)



    def end(self):
        with open(self.dataset_dir+'/train.txt', 'w') as f:
            for im in self.images_list:
                f.write(im+'\n')

        return {"out_folder": self.dataset_dir}

    def get_parameters(self):
        return {'parameters': []}

    def get_version(self):
        return _VERSION

    def blur_img(self, im, anno):
        im_blur = im

        new_anno = []
        if anno is not None:
            for bb in anno['anno']:
                if not bb['ignore'] and bb['labels'][0] != 'ignore':
                    new_anno.append(bb)
                    continue
                (l,t,r,b) = (int(bb['left']), int(bb['top']), int(bb['right']), int(bb['bottom']))
                (l,t,r,b) = self.fix_bb(l,t,r,b,im.shape)

                if (r-l)*(b-t) <= 0:
                    continue

                biggest_dim = r-l
                if (b-t) > biggest_dim:
                    biggest_dim = b-t
                kernel_size = int(biggest_dim/5.0) + (1-int(biggest_dim/5.0)%2)
                im_blur[t:b,l:r] = cv2.GaussianBlur(im_blur[t:b,l:r], (kernel_size, kernel_size), biggest_dim/5.0)


            anno['anno'] = new_anno

        return (im_blur, anno)

    def fix_bb(self, l, t, r, b, shape):
        if l<0: l=0
        if t<0: t=0
        if b>=shape[0]: b=shape[0]-1
        if r>=shape[1]: r=shape[1]-1

        return (l,t,r,b)
