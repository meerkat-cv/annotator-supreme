from flask import request, abort, session
from functools import wraps
import logging
import urllib.request as urllib2
import numpy as np
import cv2
import random
from annotator_supreme.views import error_views
from io import StringIO
from PIL import Image
from annotator_supreme import app
import os
import base64

def read_image_from_stream(stream):
    try:
        arr = np.asarray(bytearray(stream.read()), dtype=np.uint8)
        image = cv2.imdecode(arr, cv2.IMREAD_COLOR)
        height, width = image.shape[:2]
        if height <= 0 or width <= 0:
            raise Exception('Invalid image file from stream')
    except:
        raise Exception('Invalid image file from stream')

    return image


def read_image_from_url(url):
    req = urllib2.Request(url, headers={'User-Agent' : "VirtualMakeup-API"})
    res = urllib2.urlopen(req)
    if res.getcode() != 200:
        raise Exception('Invalid status code '+str(res.getcode())+' from image url')
    else:
        return read_image_from_stream(res)

def read_image_b64(base64_string):
    dec = base64.b64decode(base64_string)
    npimg = np.fromstring(dec, dtype=np.uint8)

    cvimg  = cv2.imdecode(npimg, cv2.IMREAD_COLOR)

    return cvimg

def image_to_dict(image):
    anno_vec = []
    for bb in image.bboxes:
        curr_anno = {}
        curr_anno['labels'] = bb.labels
        curr_anno['left']   = bb.left
        curr_anno['top']    = bb.top
        curr_anno['right']  = bb.right
        curr_anno['bottom'] = bb.bottom
        curr_anno['ignore'] = bb.ignore
        anno_vec.append(curr_anno)

    image_dict = {'anno': anno_vec}
    image_dict['dataset_name'] = image.dataset_name
    image_dict['name'] = image.name
    image_dict['phash'] = image.phash
    image_dict['category'] = image.category
    image_dict['partition'] = image.partition
    image_dict['fold'] = image.fold
    image_dict['last_modified'] = image.last_modified

    return image_dict


def parse_content_type(request):
    """
    This function is used to extract the content type from the header.
    """
    try:
        content_type = request.headers['content-type']
    except:
        raise error_views.InvalidParametersError('No Content-Type provided')

    json_type = 'application/json'
    data_type = 'multipart/form-data'
    lower_content_type = content_type.lower()
    if lower_content_type.find(json_type) >= 0:
        return json_type
    elif lower_content_type.find(data_type) >= 0:
        return data_type
    else:
        raise error_views.InvalidParametersError('Invalid Content-Type')


def get_param_from_request(request, label):
    """
    This function is used to extract a field from a POST or GET request.

    Returns a tuple with (ok:boolean, error:string, value)
    """
    if request.method == 'POST':
        content_type = parse_content_type(request)
        if content_type == "multipart/form-data":
            if label in request.form:
                return (True, "", request.form[label])
            else:
                return (False, "No "+label+" provided in form-data request", None)
        elif content_type == 'application/json':
            try:
                input_params = request.get_json(True)
            except:
                return (False, 'No valid JSON present', None)

            if label in input_params:
                return (True, "", input_params[label])
            else:
                return (False, "No "+label+" provided in json payload", None)
    elif request.method == 'GET':
        if request.args.get(label) == None:
            return (False, "No "+label+" in GET params", None)
        else:
            return (True, "", request.args.get(label))
    else:
        return (False, "Invalid request method", None)


def get_image_from_request(request):
    """
    This function is used to extract the image from a POST or GET request.
    Usually it is a url of the image and, in case of the POST is possible
    to send it as a multi-part data.

    Returns a tuple with (ok:boolean, error:string, image:ndarray)
    """
    if request.method == 'POST':
        content_type = parse_content_type(request)
        if content_type == "multipart/form-data":
            if 'image' in request.files:
                try:
                    image = read_image_from_stream(request.files['image'])
                    return (True, '', image)
                except:
                    return (False, "Unable to read uploaded file", None)
            else:
                return (False, "No image provided in form-data request", None)
        elif content_type == 'application/json':
            try:
                input_params = request.get_json(True)
            except:
                return (False, 'No valid JSON present', None)

            if 'imageUrl' in input_params:
                image_url = input_params['imageUrl']
                try:
                    image = read_image_from_url(image_url)
                    return (True, '', image)
                except:
                    return (False, 'Unable to read image from url', None)
            elif 'imageB64' in input_params:
                image_b64 = input_params['imageB64']
                try:
                    image = read_image_b64(image_b64)
                    return (True, '', image)
                except:
                    return (False, 'Unable to read base 64 image', None)
            else:
                return (False, 'Image url or base 64 string not informed', None)
    elif request.method == 'GET':
        if request.args.get('imageUrl') == None:
            return (False, 'Image url not informed', None)
        else:
            image_url = request.args.get('imageUrl')

        try:
            image = read_image_from_url(image_url)
            return (True, '', image)
        except:
            return (False, 'Unable to read image from url', None)
