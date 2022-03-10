import numpy as np
import platform
import cv2.cv2 as cv2
from PIL import Image
import base64
from io import BytesIO

from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync


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

def send_img(bgr_img):
    rgb_img = Image.fromarray(cv2.cvtColor(bgr_img, cv2.COLOR_BGR2RGB))
    data = BytesIO()
    rgb_img.save(data, "JPEG")
    data64 = base64.b64encode(data.getvalue())
    to_send = u'data:img/jpeg;base64,'+data64.decode('utf-8')
    state('calib', 'img', to_send)


file_name = 1

def draw_circles(img, centers, color, radius, title, wait):
    project = img.copy()
    img_size = 500
    for i in range(centers.shape[0]):
        rounded = np.round(centers[i, 0:2]).astype(int)
        if rounded[0] >= img.shape[1] or rounded[1] >= img.shape[0] or rounded[0] < 0 or rounded[1] < 0:
            continue
        c = img[rounded[1], rounded[0]].astype(float) * 0.3 + np.array(color) * 0.7
        cv2.circle(project, rounded, radius, [int(c[0]), int(c[1]), int(c[2])], -1)
    project = cv2.resize(project, (img_size, int(img_size/project.shape[1] * project.shape[0])))
    send_img(project)

def draw_circles_one_image(img, centers, color, radius, title, wait):
    project = img.copy()
    img_size = 500
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
    project = cv2.resize(project, (img_size, int(img_size/project.shape[1] * project.shape[0])))
    send_img(project)

