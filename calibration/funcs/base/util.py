import numpy as np
import platform
import cv2.cv2 as cv2

import json
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

def draw_circles(img, centers, color, radius, title, wait):
    project = img.copy()
    for i in range(centers.shape[0]):
        rounded = np.round(centers[i, 0:2]).astype(int)
        if rounded[0] >= img.shape[1] or rounded[1] >= img.shape[0] or rounded[0] < 0 or rounded[1] < 0:
            continue
        c = img[rounded[1], rounded[0]].astype(float) * 0.3 + np.array(color) * 0.7
        cv2.circle(project, rounded, radius, [int(c[0]), int(c[1]), int(c[2])], -1)
    if platform.system() == 'Windows':
        project = cv2.resize(project, (800, int(800/project.shape[1] * project.shape[0])))
    # cv2.imshow(title, project)
    # cv2.waitKey(wait)

def draw_circles_one_image(img, centers, color, radius, title, wait):
    project = img.copy()
    for cent, col in zip(centers, color):
        for i in range(cent.shape[0]):
            rounded = np.round(cent[i, 0: 2]).astype(int)
            if rounded[0] >= img.shape[1] or rounded[1] >= img.shape[0] or rounded[0] < 0 or rounded[1] < 0:
                continue
            if type(col) == type([]):
                c = img[rounded[1], rounded[0]].astype(float) * 0.3 + np.array(col) * 0.7
            else:
                c = img[rounded[1], rounded[0]].astype(float) * 0.1 + np.array([cent[i, 2], cent[i, 2], cent[i, 2]]) * 0.9

            cv2.circle(project, rounded, radius, [int(c[0]), int(c[1]), int(c[2])], -1)
    if platform.system() == 'Windows':
        project = cv2.resize(project, (800, int(800/project.shape[1] * project.shape[0])))
    # cv2.imshow(title, project)
    # cv2.waitKey(wait)

def state(id, status, msg=''):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        'cal',
        {
            'type': 'cal.msg',
            'id': id,
            'status': status,
            'msg': msg}
    )