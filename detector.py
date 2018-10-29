from utils import *
from split_img import *
from ocr import get_digit
from lineDetector import LineDetector


class Detector:
    def __init__(self):
        self.lineDetector = LineDetector()

    def __detect_big_img(self, image, char_location, line_pos, dir=None, save=True):
        for i in range(len(char_location)):
            location = char_location[i]
            digit = get_digit(image[location - 10:location + 20, -125:])
            print(digit)

            if i == len(char_location) - 1:
                detected_img = image[location:, :]
            else:
                detected_img = image[location:char_location[i + 1], :]

            if save:
                save_img(detected_img, dir, '{}.jpg'.format(digit))

            self.__detect_lines(detected_img, line_pos, digit, dir, save)

    def __detect_lines(self, image, line_pos, img_name, dir=None, save=True):
        margin = (line_pos[2] - line_pos[0]) // 2
        for i in range(3):
            pos = line_pos[i]
            line_img = image[pos:pos + margin]
            line_name = '{}-{}.jpg'.format(img_name, i + 1)
            if save:
                save_img(line_img, dir, line_name)

            line_img = cv2.cvtColor(line_img, cv2.COLOR_GRAY2BGR)
            detected_line, err_flag = self.lineDetector.detect_error_line(line_img, line_name)

            if err_flag:
                cv2.imshow(line_name, detected_line)

    def detect(self, image, target_dir):
        char_location = get_digit_position(image)

        # save_detected_img(origin_img, char_location, target_dir)
        line_pos = find_line_pos(image, char_location)

        # print(line_pos)
        self.__detect_big_img(image, char_location, line_pos, target_dir)


if __name__ == '__main__':
    dir = 'digital_img'
    target_dir = os.path.join(dir, 'split')
    if not os.path.exists(target_dir):
        os.mkdir(target_dir)

    img_name = '20180530-002.bmp'
    file = os.path.join(dir, img_name)
    origin_img = read_gray_img(file)
    origin_img = del_white(origin_img)
    # _, img = cv2.threshold(origin_img, 5, 255, cv2.THRESH_BINARY)

    origin_img = origin_img[-10000:, :]

    detector = Detector()
    detector.detect(origin_img, target_dir)

    # char_location = get_digit_position(origin_img)

    # save_detected_img(origin_img, char_location, target_dir)
    # line_pos = find_line_pos(origin_img, char_location)

    # print(line_pos)
    # detect_big_img(origin_img, char_location, line_pos, target_dir)
    # cv2.imshow('img', img)
    cv2.waitKey()
