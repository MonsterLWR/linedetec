import pytesseract
from PIL import Image
import os
import cv2
import numpy as np

# Tesseract-OCR安装目录
# path = r'C:\Program Files (x86)\Tesseract-OCR'
with open('./ocr_path.txt', 'r') as f:
    path = f.readline().strip()

pytesseract.pytesseract.tesseract_cmd = os.path.join(path, 'tesseract')

dir_path = os.path.join(path, 'tessdata')
tessdata_dir_config = r'--tessdata-dir "{}" -psm 7 digits'.format(dir_path)


def get_digit(digit_img, factor=3):
    digit_img = cv2.resize(digit_img, (int(digit_img.shape[1] * factor), int(digit_img.shape[0] * factor)))
    # kernel = np.ones((2, 2), np.uint8)
    # digit_img = cv2.dilate(digit_img, kernel)
    # digit_img = cv2.morphologyEx(digit_img, cv2.MORPH_OPEN, kernel)
    # cv2.imshow('img', digit_img)
    return pytesseract.image_to_string(digit_img, config=tessdata_dir_config)


if __name__ == '__main__':
    # print(pytesseract.image_to_string(Image.open('test2.png'), config=tessdata_dir_config))
    with open('./ocr_path.txt', 'r') as f:
        line = f.readline()
        print(line)
