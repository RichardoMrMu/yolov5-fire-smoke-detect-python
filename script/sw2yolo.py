# -*- coding:utf-8 -*-
# @Time     : 2021/7/13 17:10
# @Author   : Richardo Mu
# @FILE     : sw2yolo.py
# @Software : PyCharm

import os
import os.path
import sys
import torch
import torch.utils.data as data
import cv2
import numpy as np

try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET


def parsexml(xml_file):
    tree = ET.parse(xml_file)
    root = tree.getroot()
    filename = root.find('filename').text
    boxes = []
    classnames = []
    for obj in root.findall('object'):
        name = obj.find('name').text
        bndbox = obj.find('bndbox')
        xmin = bndbox.find('xmin').text
        ymin = bndbox.find('ymin').text
        xmax = bndbox.find('xmax').text
        ymax = bndbox.find('ymax').text
        if int(xmin) >= int(xmax) or int(ymin) >= int(ymax):
            continue
        boxes.append([int(xmin), int(ymin), int(xmax), int(ymax)])
        classnames.append(name)
    return classnames, boxes
def get_file_path(list_file_path):
    xml_path = []
    img_path = []
    with open(list_file_path,'r') as f:
        lines = f.readlines()
        count1 = 0
        
        for line in lines:
            img,xml = line.split(" ")
            xml_path.append(xml.replace("\n",""))
            img_path.append(img)
    return xml_path,img_path

list_file = "./val_list.txt"
xmls_path,imgs_path = get_file_path(list_file)

# 将train_list中的xml 转成 txt， img放到img中
save_path = './data/yolodata/fire/cocolike/val/'
root = "./data/yolodata/fire/"
train_img_root = root 

# print(os.path.dirname(train_img_root))
# imgs_path = os.listdir(train_img_root)
imgs_path = [os.path.join(train_img_root, i) for i in imgs_path]
xmls_path =  [os.path.join(train_img_root, i) for i in xmls_path]
for i in range(len(imgs_path)):
    print(i, imgs_path[i])
    img = cv2.imread(imgs_path[i])
    base_img = os.path.basename(imgs_path[i])
    base_txt = os.path.basename(imgs_path[i])[:-4] + ".txt"
    save_img_path = os.path.join(save_path, base_img)
    save_txt_path = os.path.join(save_path, base_txt)
    with open(save_txt_path, "w") as f:
        height, width, _ = img.shape
        # xml_path = imgs_path[i].replace("image", "xml_head")[:-4] + ".xml"
        xml_path = xmls_path[i]
        classnames, labels = parsexml(xml_path)
        # annotations = np.zeros((0, 14))
        if len(labels) == 0:
            continue
        for idx, label in enumerate(labels):
            annotation = np.zeros((1, 4))
            # bbox
            label[0] = max(0, label[0])
            label[1] = max(0, label[1])
            label[2] = min(width - 1, label[2])
            label[3] = min(height - 1, label[3])
            annotation[0, 0] = (label[0] + (label[2] -label[0]) / 2) / width  # cx
            annotation[0, 1] = (label[1] + (label[3]-label[1]) / 2) / height  # cy
            annotation[0, 2] = (label[2] -label[0]) / width  # w
            annotation[0, 3] = (label[2] -label[0]) / height  # h
            str_label = "0" if classnames[idx] == "fire" else "1"

            for i in range(len(annotation[0])):
                str_label = str_label + " " + str(annotation[0][i])
            str_label = str_label.replace('[', '').replace(']', '')
            str_label = str_label.replace(',', '') + '\n'
            f.write(str_label)
    cv2.imwrite(save_img_path, img)
