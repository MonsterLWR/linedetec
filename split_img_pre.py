import cv2
import os


def del_white(img):
    width = img.shape[1]
    pos = width // 2
    while img[0][pos] == 255:
        img = img[1:, :]
    while img[-1][pos] == 255:
        img = img[:-1, :]
    return img


# def split_reverse(img, start, end, target_dir, line_beg=270, line_height=150):
#     img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
#     img = del_white(img)
#
#     height = img.shape[0]
#     width = img.shape[1]
#     print(img.shape[0])
#     # print(img.shape[1])
#     count = start - end + 1
#     height_per_img = round(height / count)
#     print(height_per_img)
#     for i in range(count):
#         base_name = i + 1
#         beg = (count - i - 1) * height_per_img
#         splited_img = img[beg:beg + height_per_img, :]
#         splited_img1 = splited_img[line_beg:line_beg + line_height, :]
#         splited_img2 = splited_img[line_beg + line_height:line_beg + 2 * line_height, :]
#         splited_img3 = splited_img[line_beg + 2 * line_height:, :]
#         cv2.imwrite(os.path.join(target_dir, '{}.jpg'.format(base_name)), splited_img)
#         # cv2.imwrite(os.path.join(target_dir, '{}-{}.jpg'.format(base_name, 1)), splited_img1)
#         # cv2.imwrite(os.path.join(target_dir, '{}-{}.jpg'.format(base_name, 2)), splited_img2)
#         # cv2.imwrite(os.path.join(target_dir, '{}-{}.jpg'.format(base_name, 3)), splited_img3)


def split(img, start, end, target_dir, line_beg=270, line_height=150):
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    img = del_white(img)
    img = img[540:, :]

    height = img.shape[0]
    width = img.shape[1]
    print(img.shape[0])
    # print(img.shape[1])
    count = start - end + 1
    height_per_img = round(height / count)
    print(height_per_img)
    for i in range(count):
        base_name = start - i
        beg = i * height_per_img
        splited_img = img[beg:beg + height_per_img, :]
        splited_img1 = splited_img[line_beg:line_beg + line_height, :]
        splited_img2 = splited_img[line_beg + line_height:line_beg + 2 * line_height, :]
        splited_img3 = splited_img[line_beg + 2 * line_height:, :]
        # cv2.imwrite(os.path.join(target_dir, '{}.jpg'.format(base_name)), splited_img)
        cv2.imwrite(os.path.join(target_dir, '{}-{}.jpg'.format(base_name, 1)), splited_img1)
        cv2.imwrite(os.path.join(target_dir, '{}-{}.jpg'.format(base_name, 2)), splited_img2)
        cv2.imwrite(os.path.join(target_dir, '{}-{}.jpg'.format(base_name, 3)), splited_img3)


if __name__ == '__main__':
    dir = 'digital_img'
    target_dir = os.path.join(dir, 'split')
    if not os.path.exists(target_dir):
        os.mkdir(target_dir)

    img_name = '20180530-002.bmp'
    # img_name = '36.jpg'
    file = os.path.join(dir, img_name)
    img = cv2.imread(file)

    # img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # img = del_white(img)
    #
    # cv2.imwrite(os.path.join(target_dir, img_name), img)

    # print(img.shape[0])
    # print(img.shape[1])
    # 720 270 150
    # 660 20 180
    # img1 = img[270:420, :]
    # img2 = img[420:570, :]
    # img3 = img[570:, :]
    # cv2.imshow('img1', img1)
    # cv2.imshow('img2', img2)
    # cv2.imshow('img3', img3)
    # cv2.waitKey()
    #
    split(img, 370, 1, target_dir, line_beg=20, line_height=180)
