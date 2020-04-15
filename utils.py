import os
import cv2

def read_gray_img(img_file):
    """读取灰度化后的图片"""
    img = cv2.imread(img_file,cv2.IMREAD_GRAYSCALE)
    # img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    return img


def save_img(saved_img, dir, img_name):
    cv2.imwrite(os.path.join(dir, img_name), saved_img)
