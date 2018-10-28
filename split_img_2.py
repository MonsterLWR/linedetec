import os
import cv2
import numpy as np
import matplotlib.pyplot as plt
from ocr import get_digit


def read_img(img_file):
    """读取二值化后并且去除白边的图片"""
    img = cv2.imread(img_file)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    img = del_white(img)
    return img


def del_white(img):
    """清除二值化后图片的白边"""
    width = img.shape[1]
    pos = width // 2
    while img[0][pos] == 255:
        img = img[1:, :]
    while img[-1][pos] == 255:
        img = img[:-1, :]
    return img


def save_img(saved_img, dir, img_name):
    cv2.imwrite(os.path.join(dir, img_name), saved_img)


def segment(img):
    """将输入的大图片按照数字标识出现的位置进行分割
        """
    width = img.shape[1]
    pos = width // 2

    # cv2.imshow('img', img)

    # 根据像素在垂直方向上的投影判断数字标识的出现
    pix_sum = np.sum(img[:, pos:], axis=1)
    pix_sum_bool = np.logical_and(15000 > pix_sum, pix_sum > 2000)
    char_location = []
    pre_bool = False
    bool_count = 0
    for i, bool in enumerate(pix_sum_bool):
        if not pre_bool and bool:
            # False -> True
            bool_count = 1
        elif pre_bool and bool:
            # True -> True
            bool_count += 1
        elif pre_bool and not bool:
            # True -> False
            if bool_count >= 10:
                # 排除很短的断线的影响
                location = i - bool_count
                xs = np.where(img[location, :] > 0)[0]
                dig_len = xs[-1] - xs[0]
                if 80 < dig_len < 120:
                    # 找到了标识的数字,记录其在垂直方向上的位置
                    char_location.append(location)
                    digit = img[location - 10:location + 20, -125:]
                    # _, digit = cv2.threshold(digit, 40, 255, cv2.THRESH_BINARY_INV)
                    print(get_digit(digit))
            bool_count = 0
        pre_bool = bool

    print(len(char_location))
    return char_location

    # plt.plot(pix_sum)
    # plt.show()
    # cv2.waitKey()


if __name__ == '__main__':
    dir = 'digital_img'
    target_dir = os.path.join(dir, 'split-4')
    if not os.path.exists(target_dir):
        os.mkdir(target_dir)

    img_name = '20180730-002.bmp'
    # img_name = '36.jpg'
    file = os.path.join(dir, img_name)
    origin_img = read_img(file)
    _, img = cv2.threshold(origin_img, 5, 255, cv2.THRESH_BINARY)

    # print(img.shape)
    # img = img[190000:, :]
    # print(img.shape)
    char_location = segment(img)
    # cv2.waitKey()
    # for i in range(len(char_location)):
    #     if i == len(char_location) - 1:
    #         save_img(origin_img[char_location[i]:, :], target_dir, '{}.jpg'.format(i))
    #         break
    #     save_img(origin_img[char_location[i]:char_location[i + 1], :], target_dir, '{}.jpg'.format(i))
