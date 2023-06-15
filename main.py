from pathlib import Path 
import argparse
import os 
import numpy as np
from scipy.optimize import linear_sum_assignment
import cv2

        
im_W = 720
im_H = 576

def readfiles():
    parser = argparse.ArgumentParser()
    parser.add_argument('dir', type=str)
    args = parser.parse_args()
    path_img = args.dir + "/frames/"
    path_boxes = args.dir + "/bboxes.txt"
    imgs = read_imgs(path_img)
    bbs = read_bboxes(path_boxes)
    return imgs, bbs

def read_imgs(path):
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
                bb['boxes'].append(np.asarray(lines[k][:-1].split(' '), np.float32))
            bbs.append(bb)
        else:
            continue
    return bbs

def dist_score(frame1 : dict, frame2 : dict):
    f1 = []
    f2 = []
    
    for i in frame1['boxes']: 
        f1.append(((i[0]+i[2]/2)/im_W, (i[1]+ i[3]/2)/im_H))
    for i in frame2['boxes']: 
        f2.append(((i[0]+i[2]/2)/im_W, (i[1]+ i[3]/2)/im_H))
    x = np.zeros([len(f1), len(f2)])
    for k in range(0,len(f1)):
        for j in range(0,len(f2)):
            x[k,j] = np.sqrt(pow(f1[k][0] - f2[j][0], 2) + pow(f1[k][1] - f2[j][1], 2))
    return x

def hist_score(img1, img2, bboxes1, bboxes2):
    people1 = []
    people2 = []
    for b in bboxes1['boxes']:
        people1.append(img1[int(b[1]):int(b[1]+b[3]), int(b[0]):int(b[0]+b[2])])
    for b in bboxes2['boxes']:
        people2.append(img2[int(b[1]):int(b[1]+b[3]), int(b[0]):int(b[0]+b[2])])
    x = np.zeros((len(people1), len(people2)))
    for k in range(0,len(people1)):
        for j in range(0,len(people2)):
            hist1 = cv2.calcHist([people1[k]],[0, 1, 2], None, [8, 8, 8],
		[0, 256, 0, 256, 0, 256])
            hist2 = cv2.calcHist([people2[j]],[0, 1, 2], None, [8, 8, 8],
		[0, 256, 0, 256, 0, 256])
            x[k,j] = 1 - cv2.compareHist(hist1, hist2, cv2.HISTCMP_CORREL)
    return x

def size_score(frame1, frame2, bboxes1, bboxes2):
    h1, _, _ = frame1.shape
    h2, _ , _ = frame2.shape
    area1 = []
    area2 = []
    for b in bboxes1['boxes']:
        area1.append(10*b[3]/h1)
    for b in bboxes2['boxes']:
        area2.append(10*b[3]/h2)
    x = np.zeros((len(area1), len(area2)))
    for k in range(0,len(area1)):
        for j in range(0,len(area2)):
            x[k,j] = np.abs(area1[k]-area2[j])
    return x

def addition_scores(hist, dist, size):
    score = 0.8*hist+0.2*dist+ 0.2*size
    if score.shape[0] == score.shape[1]:
        newrow = []
        for s in range(0, score.shape[1]):
            newrow.append(0.7)
        score = np.vstack([score, newrow])
    return score

def calc_score(frame1 : dict, frame2 : dict, img1, img2):

    distance = dist_score(frame1, frame2)
    # print("dist \n", distance)
    pips = hist_score(img1, img2, frame1, frame2)
    # print("hist \n", pips)
    size = size_score(img1, img2, frame1, frame2)
    scor = addition_scores(distance, pips, size)
    # print("cost matrix", scor)
    score = linear_sum_assignment(scor)
    return score, scor


def get_results(score, cost_m):
    row_ind, col_ind = score
    results = []
    x = cost_m.shape[1]
    for i in range(0, x):
        results.append(-1)
    
    for i in range(0, len(col_ind)):
        k = col_ind[i]
        if cost_m[row_ind[i], col_ind[i]] < 0.55:
            results[k] = row_ind[i]
    res = ''
    for i in results:
        res+= str(i) + ' '
    print(res)
    return results

def show_frames( frame1, frame2, bbox1, bbox2):
    frs = [frame1.copy(), frame2.copy()]
    bboxs = [bbox1['boxes'], bbox2['boxes']]
    for i in range(0, len(bboxs[0])):
        cv2.rectangle(frs[0], (int(bboxs[0][i][0]),int(bboxs[0][i][1])), (int(bboxs[0][i][0]+bboxs[0][i][2]), int(bboxs[0][i][1]+bboxs[0][i][3])), (200,0,0), 3)
        cv2.putText(frs[0], str(i), (int(bboxs[0][i][0]),int(bboxs[0][i][1])), cv2.FONT_HERSHEY_COMPLEX, 1, (128, 128, 128), 2, cv2.LINE_8)
    for j in range(0, len(bboxs[1])):
        cv2.rectangle(frs[1], (int(bboxs[1][j][0]),int(bboxs[1][j][1])), (int(bboxs[1][j][0]+bboxs[1][j][2]), int(bboxs[1][j][1]+bboxs[1][j][3])), (200,0,0), 3)
        cv2.putText(frs[1], str(j), (int(bboxs[1][j][0]),int(bboxs[1][j][1])), cv2.FONT_HERSHEY_COMPLEX, 1, (128, 128, 128), 2, cv2.LINE_8)
    return frs       




pics, bboxes = readfiles()
r = len(bboxes)

for i in range(0, r):
    if i == 0:
        res = ''
        for j in range(0,len(bboxes[i]['boxes'])):
            res += "-1 "
        print(res)
    else:
        score, cost_matrix = calc_score(bboxes[i-1], bboxes[i], pics[i-1], pics[i])
        results = get_results(score, cost_matrix)

