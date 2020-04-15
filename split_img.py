import numpy as np
import cv2
#import matplotlib.pyplot as plt


def get_digit_position(img):
    """返回将输入的大图片中数字标识出现的位置"""
    width = img.shape[1]
    pos = width // 2

    # 根据像素在垂直方向上的投影判断数字标识的出现
    zero_one_img = (img[:, pos:])
    zero_one_img = zero_one_img >= 200
    pix_sum = np.sum(zero_one_img, axis=1)
    # plt.plot(pix_sum)
    # plt.show()
    pix_sum_bool = np.logical_and(50 > pix_sum, pix_sum > 10)
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
                    char_location.append(location - 1)
                    # digit = img[location - 10:location + 20, -125:]
                    # print(get_digit(digit))
            bool_count = 0
        pre_bool = bool

    print('total_img:{}'.format(len(char_location)))
    return char_location


def find_line_pos(image, char_location):
    """根据image和对应的char_location，找到用于分割线的line_pos"""
    line_pos = []
    # pos_flag = False
    # i = 0
    # while not pos_flag:
    #     img = image[char_location[i]:char_location[i + 1], :]
    #     pos_flag, line_pos = get_line_position(img)
    #     i += 1
    pos_num = 3
    while pos_num != 0:
        for i in range(len(char_location) - 1):
            img = image[char_location[i]:char_location[i + 1], :]
            pos_flag, line_pos = get_line_position(img, pos_num)
            if pos_flag:
                break

        if len(line_pos) > 0:
            break
        pos_num -= 1

    if len(line_pos) == 0:
        raise ValueError("can't calculate line_pos!")

    return line_pos


def cal_margin(line_pos):
    if len(line_pos) > 1:
        return (line_pos[-1] - line_pos[0]) // (len(line_pos) - 1)
    elif len(line_pos) == 1:
        return line_pos[0]
    else:
        raise ValueError("wrong line_pos!")


def get_line_position(image, pos_num=3):
    """输入一张已经按数字标号分割出来的灰度化图片，获取该图片中三条线的位置
        返回True代表该图中找到的线的位置具有普适性，可以用于分割其他图片中的线"""
    # cv2.imshow('image', image)
    # cv2.waitKey()
    left_ver_line = image[:, 0]
    left_line_pos = []
    pre_v = 0
    for i, v in enumerate(left_ver_line):
        # 线的上边界
        if pre_v < 10 and v >= 10:
            left_line_pos.append(i)
        pre_v = v

    right_ver_line = image[:, -1]
    right_line_pos = []
    pre_v = 0
    for i, v in enumerate(right_ver_line):
        # 线的上边界
        if pre_v < 10 and v >= 10:
            right_line_pos.append(i)
        pre_v = v

    # 判断该图中线的位置是否普适，即线的左右位置是否对其，是否一共有pos_num根线
    line_pos = []
    if len(left_line_pos) == pos_num and len(right_line_pos) == pos_num:
        for i in range(len(left_line_pos)):
            if abs(left_line_pos[i] - right_line_pos[i]) > 20:
                return False, line_pos
        # margin = cal_margin(left_line_pos)
        for pos in left_line_pos:
            # temp_pos = pos - round(margin * 0.5)
            # if temp_pos < 0:
            #     # skip掉包含数字的区域
            #     temp_pos = 30
            line_pos.append(pos)
        return True, line_pos
    else:
        return False, line_pos
