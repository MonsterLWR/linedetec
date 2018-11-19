from utils import *
from split_img import *
from ocr import get_digit
from lineDetector import LineDetector
import tkinter as tk


class Detector:
    def __init__(self, text_widget=None, err_choice=None):
        self.lineDetector = LineDetector(verbose=False, err_choice=err_choice)
        self.text_widget = text_widget
        self.__clear_text_widget()
        self.__add_text_widget('开始检测，请耐心等待...\n')

    def __clear_text_widget(self):
        if self.text_widget is not None:
            self.text_widget['state'] = 'normal'
            self.text_widget.delete('1.0', tk.END)
            self.text_widget['state'] = 'disabled'

    def __add_text_widget(self, str):
        if self.text_widget is not None:
            self.text_widget['state'] = 'normal'
            self.text_widget.insert(tk.END, str)
            self.text_widget['state'] = 'disabled'
            self.text_widget.see('end')

    def __del_white(self, img):
        """清除灰度化后图片的白边，以及大图片中间的白块"""
        print(img.shape)
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

    def __detect_big_img(self, image, char_location, line_pos, dir=None, save=False):
        err_dir = os.path.join(dir, 'err_lines')
        if not os.path.exists(err_dir):
            os.mkdir(err_dir)

        lines_dir = None
        if save:
            lines_dir = os.path.join(dir, 'lines')
            if not os.path.exists(lines_dir):
                os.mkdir(lines_dir)

        with open(os.path.join(dir, 'err.txt'), 'a') as f:
            for i in range(len(char_location)):
                location = char_location[i]
                digit = get_digit(image[location - 10:location + 20, -125:])
                print(digit)

                if i == len(char_location) - 1:
                    detected_img = image[location:, :]
                else:
                    detected_img = image[location:char_location[i + 1], :]

                if save:
                    save_img(detected_img, lines_dir, '{}.jpg'.format(digit))

                self.__detect_lines(detected_img, line_pos, digit, lines_dir, err_dir, f, save)

            self.__add_text_widget('检测完成\n')
            # if self.text_widget is not None:
            #     self.text_widget['state'] = 'normal'
            #     self.text_widget.insert(tk.END, )
            #     self.text_widget['state'] = 'disabled'
            #     self.text_widget.see('end')

    def __detect_lines(self, image, line_pos, img_name, lines_dir=None, err_dir=None, err_txt=None, save=False):
        margin = (line_pos[2] - line_pos[0]) // 2
        for i in range(3):
            pos = line_pos[i]
            line_img = image[pos:pos + margin]
            line_name = '{}-{}.jpg'.format(img_name, i + 1)
            base_name, _ = os.path.splitext(line_name)

            if save:
                save_img(line_img, lines_dir, line_name)

            self.__add_text_widget('正在检测{}\n'.format(base_name))
            # if self.text_widget is not None:
            #     self.text_widget['state'] = 'normal'
            #     self.text_widget.insert(tk.END, )
            #     self.text_widget['state'] = 'disabled'
            #     self.text_widget.see('end')

            line_img = cv2.cvtColor(line_img, cv2.COLOR_GRAY2BGR)
            detected_line, err_flag = self.lineDetector.detect_error_line(line_img, line_name)

            if err_flag:
                save_img(detected_line, err_dir, line_name)
                print(base_name, file=err_txt)
                # cv2.imshow(line_name, detected_line)

    def detect(self, image_path, target_dir):
        """检测image_path大图片中的异常，在target_dir中生成检测结果"""
        image = read_gray_img(image_path)
        image = self.__del_white(image)

        char_location = get_digit_position(image)

        # save_detected_img(origin_img, char_location, target_dir)
        line_pos = find_line_pos(image, char_location)

        # print(line_pos)
        self.__detect_big_img(image, char_location, line_pos, target_dir, save=True)


if __name__ == '__main__':
    dir = 'digital_img'
    target_dir = os.path.join(dir, '20180602-001')
    if not os.path.exists(target_dir):
        os.mkdir(target_dir)

    img_name = '20180602-001.bmp'
    file = os.path.join(dir, img_name)
    # origin_img = read_gray_img(file)
    # origin_img = del_white(origin_img)
    # _, img = cv2.threshold(origin_img, 5, 255, cv2.THRESH_BINARY)

    # origin_img = origin_img[-10000:, :]

    detector = Detector()
    detector.detect(file, target_dir)

    # char_location = get_digit_position(origin_img)

    # save_detected_img(origin_img, char_location, target_dir)
    # line_pos = find_line_pos(origin_img, char_location)

    # print(line_pos)
    # detect_big_img(origin_img, char_location, line_pos, target_dir)
    # cv2.imshow('img', img)
    # cv2.waitKey()
