import requests
import json
import os
import cv2
import numpy as np
from requests_toolbelt import MultipartEncoder


HOST       = 'http://localhost/annotator-supreme'
train_file = '/media/meerkat/Data/datasets/logo_kairos/nascar_remote/blurred/nascar_brands_train_full_pure.txt'

tags = [ 'Alpinestars', 'Bank_of_America', 'Bugles', 'CarQuest', 'Cheezit', 'Chevrolet', 'DuPont', 'Ford', 'GM', 'Goodwrench', 'KBB', 'Kellogs', 'Nascar', 'PopTarts', 'QuakerState', 'Sprint', 'Strohs_Light', 'Toyota', 'Valvoline', 'Wrangler']

res = requests.post(HOST+'/dataset/create', json={'name': 'nascar2', 'tags':tags})

with open(train_file) as f:
    content = f.readlines()
content = [x.strip() for x in content]

num_imgs = 0
for im in content:
    num_imgs += 1
    labels_file = os.path.splitext(im)[0]+'.txt'
    with open(labels_file) as f:
        content2 = f.readlines()

    m = MultipartEncoder(
            fields={'image': ('filename', open(im, 'rb'))}
    )
    res = requests.post(HOST+'/image/nascar2/add', data=m, headers={'Content-Type': m.content_type})
    if res.status_code != 200:
        continue

    res = res.json()
    first_line = content2[0].split()
    class_id = int(first_line[0])
    # if (res['imageId'] == '0b78334720c0b108d31322ac5221ada6'):
    #     print(res)
    #     print(content2)
    #     print('label', tags[class_id])

    im_cv  = cv2.imread(im)
    height = im_cv.shape[0]
    width  = im_cv.shape[1]
    anno_vec = []
    for curr_line in content2:
        line_split = curr_line.split()
        (x, y, w, h) = (float(line_split[1]), float(line_split[2]), float(line_split[3]), float(line_split[4]))
        (l, t, r, b) = ((x-w/2)*width, (y-h/2)*height, (x+w/2)*width, (y+h/2)*height)
        label = tags[class_id]
        anno_vec.append({'left':l, 'top':t, 'right':r, 'bottom':b, 'labels':[label], 'ignore': False})

    res = requests.post(HOST+'/image/anno/'+res['imageUrl'], json={'anno': anno_vec})
    print(im)

    # if num_imgs >= 2:
    #     exit()
