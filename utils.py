import os
import cv2
import numpy as np


def read_gray_img(img_file):
    """读取灰度化后的图片"""
    img = cv2.imread(img_file)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    return img


def del_white(img):
    """清除灰度化后图片的白边，以及大图片中间的白块"""
    width = img.shape[1]
    pos = width // 2
    while img[0][pos] >= 240:
        img = img[1:, :]
    while img[-1][pos] >= 240:
        img = img[:-1, :]

    # 删除大图片中间的白块
    vertical_line = img[:, 0]
    white_lines = np.where(vertical_line >= 240)
    img = np.delete(img, white_lines, axis=0)

    return img


def save_img(saved_img, dir, img_name):
    cv2.imwrite(os.path.join(dir, img_name), saved_img)
