from pathlib import Path 
import argparse
import os 
import pprint
import numpy as np
import collections
from hungarian_algorithm import algorithm
import cv2
from skimage import exposure
from skimage.exposure import match_histograms
        
im_W = 720
im_H = 576

def read_imgs(path):
    # parser = argparse.ArgumentParser()
    # parser.add_argument('images_dir', type=str)
    # parser.add_argument('results_file', type=str)
    # args = parser.parse_args()
    imgs = []
    images_dir = Path(path)
    images_paths = sorted([image_path for image_path in images_dir.iterdir() if image_path.name.endswith('.jpg')])
    for image_path in images_paths:
        image = cv2.imread(str(image_path))
        if image is None:
            print(f'Error loading image {image_path}')
            continue
        imgs.append(image)
    return imgs

def read_bboxes(path):
    file1 = open(path, 'r')
    lines = file1.readlines()
    bbs = []
    for i in range(0, len(lines)):
        bb = {}
        if (lines[i].find(".jpg")) != -1:
            bb['name'] = lines[i][:-1]
            num = int(lines[i+1])
            bb['boxes'] = []
            for k in range(i+2, i+2+num):
                bb['boxes'].append(lines[k][:-1])
            bbs.append(bb)
        else:
            continue
    return bbs

def dist_score(frame1 : dict, frame2 : dict):
    f1 = []
    f2 = []
    x = collections.defaultdict(dict)

    for i in frame1['boxes']: 
        # f1.append(np.asarray(i.split(' '), np.float32))
        arr = np.asarray(i.split(' '), np.float32)
        f1.append(((arr[0]+arr[2]/2)/im_W, (arr[1]+ arr[3]/2)/im_H))
    for i in frame2['boxes']: 
        # f2.append(np.asarray(i.split(' '), np.float32))
        arr = np.asarray(i.split(' '), np.float32)
        f2.append(((arr[0]+arr[2]/2)/im_W, (arr[1]+ arr[3]/2)/im_H))
    # x = np.zeros([len(f1), len(f2)])
    for k in range(0,len(f1)):
        for j in range(0,len(f2)):
            # x[k,j] = np.sqrt(pow(f1[k][0] - f2[j][0], 2) + pow(f1[k][1] - f2[j][1], 2))
            x[str(j)+ 'c'][str(k)+ 'r'] = np.sqrt(pow(f1[k][0] - f2[j][0], 2) + pow(f1[k][1] - f2[j][1], 2))
    return dict(x)

def hist_score(img1, img2, bboxes1, bboxes2):
    people1 = []
    people2 = []
    x = collections.defaultdict(dict)
    for b in bboxes1['boxes']:
        print(b)
        b = np.asarray(b.split(' '), np.float32)
        people1.append(img1[int(b[1]):int(b[1]+b[3]), int(b[0]):int(b[0]+b[2])])
    for b in bboxes2['boxes']:
        print(b)
        b = np.asarray(b.split(' '), np.float32)
        people2.append(img2[int(b[1]):int(b[1]+b[3]), int(b[0]):int(b[0]+b[2])])

    for k in range(0,len(people1)):
        for j in range(0,len(people2)):
            hist1 = cv2.calcHist([people1[k]],[0],None,[256],[0,256])
            hist2 = cv2.calcHist([people2[j]],[0],None,[256],[0,256])
            x[str(j)+ 'c'][str(k)+ 'r'] = 1 - cv2.compareHist(hist1, hist2, cv2.HISTCMP_CORREL)
    print(dict(x))
    return dict(x)

def addition_scores(hist_dict : dict, dist_dict : dict):
    for key, val in hist_dict.items():
        for key2, val2 in val.items():
            dist_dict[key][key2] = dist_dict[key][key2] + val2
    return dist_dict

def calc_score(frame1 : dict, frame2 : dict, img1, img2):

    distance = dist_score(frame1, frame2)
    pips = hist_score(img1, img2, frame1, frame2)
    scor = addition_scores(distance, pips)
    score = algorithm.find_matching(scor, matching_type = 'min', return_type = 'list')
    print(score)
        



p = os.getcwd()
p_boxes = p + "/sampledata/bboxes.txt"
p_im = p + "/sampledata/frames/"
bboxes = read_bboxes(p_boxes)
pics = read_imgs(p_im)
r = len(bboxes)

# for i in range(1, r):
#     calc_score(bboxes[i-1], bboxes[i])
calc_score(bboxes[-4], bboxes[-3], pics[-4], pics[-3])
# pprint.pprint(bboxes)