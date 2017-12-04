import requests
import json
from requests_toolbelt import MultipartEncoder
from lxml import etree
import re 
import sys

_annotator_url = 'http://localhost/annotator-supreme'
_dataset_name = 'default'
_image_category = "cars"

def create_dataset(dataset_name):
    global _dataset_name
    _dataset_name = dataset_name
    r = requests.post(_annotator_url+'/dataset/create', 
                      json={'name': _dataset_name,
                            'tags':[ 'alpr']})
    return(r)


def insert_image(image_name,image_path,category):
    m = MultipartEncoder(
        fields={'image': ('filename', open(image_path, 'rb')),
                'category': category, 
                'name': image_name}
    )
    r = requests.post(_annotator_url+"/image/"+_dataset_name+"/add",
                      data=m, 
                      headers={'Content-Type': m.content_type}  )
    return(r)


def insert_annotation(image_id,annotation_json):
    r = requests.post(_annotator_url+'/image/anno/'+_dataset_name+'/'+image_id,
                      json=annotation_json)
    return r


if __name__ == '__main__':

    file_name = str(sys.argv[1])
    print("Reading dataset from: ", file_name)

    tree = etree.parse(file_name)
    root = tree.getroot()

    dataset_name = root.xpath('name/text()')[0]
    r = create_dataset(dataset_name)
    print(r.text)

    # matches license plates AAA-DDDD
    plate = re.compile('.*([a-zA-Z][a-zA-Z][a-zA-Z]-\d\d\d\d).*',re.IGNORECASE)

    for child in root.xpath('images/image'):
        image_path = child.attrib['file']
        image_name = image_path.split("/")[-1]

        #add the image 
        r = insert_image(image_name,image_path,_image_category)
        print(r.text)
        image_id = r.json()['imageId']
        
        #adds annotations to image just inserted
        labelList = plate.findall(image_name)

        boxList =  [ dict(i.attrib) for i in child.xpath('box')] 
    
        annotList = [ { 'top': int(d['top']) , 
                        'left': int(d['left']), 
                        'right': int(d['left'])+int(d['width']),
                        'bottom': int(d['top'])+int(d['height']),
                        'labels': labelList, 
                        'ignore':  bool(d['ignore'] if 'ignore' in d else False ) }
                      for d in boxList ]  

        annotation_json = { 'anno' : annotList} 
        
        r = insert_annotation(image_id,annotation_json)
        
        print(image_name,": ",r.status_code)
