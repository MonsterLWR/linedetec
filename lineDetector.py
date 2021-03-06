# coding=utf-8
import numpy as np
import cv2


class LineDetector:
    def __init__(self, margin=5, threshold=100, sample_count_per_hundred=50, verbose=True, show=False,
                 err_choice=None):
        self.err_choice = err_choice
        self.margin = margin
        self.threshold = threshold
        self.verbose = verbose
        self.sample_count_per_hundred = sample_count_per_hundred
        self.sec_size = round(sample_count_per_hundred / 2)
        self.show = show

    def __pre_process(self, img, threshold):
        """对img做预处理，二值化"""
        # 灰度化
        gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        # 二值化
        _, pre_img = cv2.threshold(gray_img, threshold, 255, cv2.THRESH_BINARY_INV)
        return gray_img, pre_img

    def __del_margin(self, img, margin, direction):
        """从img中去掉像素宽度为margin,方向为direction的边缘部分"""
        if direction == 'up':
            img = img[margin:, :]
        elif direction == 'down':
            img = img[:-margin, :]
        elif direction == 'left':
            img = img[:, margin:]
        elif direction == 'right':
            img = img[:, :-margin]
        elif direction == 'up_down':
            img = img[margin:-margin, :]
        elif direction == 'left_right':
            img = img[:, margin:-margin]
        return img

    def __del_white_margin(self, img, margin):
        """删除img中边缘的白边，返回处理后的img和删除边缘产生的offset（用于后续画图）"""
        offset = {'x': 0, 'y': 0}
        upper_left = img[0][0]
        upper_right = img[0][-1]
        lower_left = img[-1][0]
        lower_right = img[-1][-1]
        while upper_left == 0 and upper_right == 0 and lower_left == 0 and lower_right == 0:
            if img[0][img.shape[1] // 2] == 0:
                offset['y'] += margin
                img = self.__del_margin(img, margin, 'up_down')
                upper_left = img[0][0]
                upper_right = img[0][-1]
                lower_left = img[-1][0]
                lower_right = img[-1][-1]
            else:
                offset['x'] += margin
                img = self.__del_margin(img, margin, 'left_right')
                upper_left = img[0][0]
                upper_right = img[0][-1]
                lower_left = img[-1][0]
                lower_right = img[-1][-1]
        while upper_left == 0 and upper_right == 0:
            offset['y'] += margin
            img = self.__del_margin(img, margin, 'up')
            upper_left = img[0][0]
            upper_right = img[0][-1]
        while upper_left == 0 and lower_left == 0:
            offset['x'] += margin
            img = self.__del_margin(img, margin, 'left')
            upper_left = img[0][0]
            lower_left = img[-1][0]
        while lower_left == 0 and lower_right == 0:
            img = self.__del_margin(img, margin, 'down')
            lower_left = img[-1][0]
            lower_right = img[-1][-1]
        while upper_right == 0 and lower_right == 0:
            img = self.__del_margin(img, margin, 'right')
            upper_right = img[0][-1]
            lower_right = img[-1][-1]
        return img, offset

    def __get_info(self, img, gray, step):
        """计算二值化后img中的，以step为间距的采样的列上线的宽度，线的边界数和线距离顶部的长度"""
        # widths:保存每个采样的列上，线的宽度
        # edge_counts:保存每个采样的列上，线的边界个数
        # first_edge_dis:保存每个采样的列上，第一个边界距离图像顶部的像素长度
        # vatys:保存每个采样的列上，线宽度的连续变化
        info = {'widths': [], 'edge_counts': [], 'first_edge_dis': [], 'varys': [],
                'img_height': img.shape[0],
                'img_width': img.shape[1]}

        pos = 0
        while pos < info['img_width']:
            col = img[:, pos]
            width = 0
            pre_pixel = 255
            # 该列上线的边界个数
            count = 0
            # 该列上的第一个边界距离图像顶部的像素长度
            dis = 0
            for pixel in col:
                if pixel != pre_pixel:
                    count += 1
                if count == 0:
                    dis += 1
                if pixel == 0:
                    width += 1
                pre_pixel = pixel
            info['edge_counts'].append(count)
            info['first_edge_dis'].append(dis)
            info['widths'].append(width)
            pos += step
        info['varys'] = self.__get_varys(info['widths'], self.sec_size)
        info['slopes'] = self.__get_slopes(info['first_edge_dis'], self.sec_size)
        info['brightness_max'] = self.__get_brightness(gray)
        if self.verbose:
            print('edge_counts:{}'.format(info['edge_counts']))
            print('first_edge_dis:{}'.format(info['first_edge_dis']))
            print('slopes:{}'.format(info['slopes']))
            print('widths:{}'.format(info['widths']))
            print('varys:{}'.format(info['varys']))
            print('brightness_max:max:{},min:{}'.format(max(info['brightness_max']), min(info['brightness_max'])))
            # print('brightness:{}'.format(info['brightness']))
        return info

    def __get_slopes(self, first_edge_dis, sec_size):
        slopes = []
        slopes_sec = []
        pre_dis = 0
        for i, dis in enumerate(first_edge_dis):
            if i == 0:
                pre_dis = dis
                continue
            slope = dis - pre_dis
            slopes.append(slope)
            pre_dis = dis

        # if self.verbose:
        #     print('slopes_before:{}'.format(slopes))
        # slopes_sec = [slo + slopes[i + 1] for i, slo in enumerate(slopes) if i + 1 < len(slopes)]
        slope_sec = 0
        for i in range(len(slopes)):
            if not i + sec_size - 1 < len(slopes):
                break
            # slope_sec = 0
            if i == 0:
                for j in range(sec_size):
                    slope_sec += slopes[j]
            else:
                slope_sec -= slopes[i - 1]
                slope_sec += slopes[i - 1 + sec_size]
            slopes_sec.append(slope_sec)

        # print('varys:{}'.format(varys))
        # print(varys.index(max(varys)))
        # abs_slopes = [abs(slope) for slope in slopes]
        return slopes_sec

    def __get_varys(self, widths, sec_size):
        # 两函数逻辑相同
        return self.__get_slopes(widths, sec_size)

    def __find_error(self, origin_img, offset, info, step, var_limit, width_limit_max,
                     width_limit_min, slope_limit, variation_limit, big_vary_count, brightness_limit):
        """在原图标识出出错的线，返回标识后的图片和是否进行过标识"""

        # 断线异常影响后续异常的检测，若检测到断线异常则直接返回。
        # 检测是否存在断线
        pre_width = 0
        flag = False
        for i, width in enumerate(info['widths']):
            if i == 0:
                pre_width = width
            if pre_width == 0 and width != 0:
                flag = True
                # 画红圈
                cv2.circle(origin_img,
                           (offset['x'] + i * step,
                            offset['y'] + info['first_edge_dis'][i] + info['widths'][i] // 2),
                           30,
                           (0, 0, 255),
                           1)
            elif pre_width != 0 and width == 0:
                flag = True
                # 画红圈
                cv2.circle(origin_img, (
                    offset['x'] + (i - 1) * step,
                    offset['y'] + info['first_edge_dis'][i - 1] + info['widths'][i - 1] // 2),
                           30,
                           (0, 0, 255),
                           1)
            pre_width = width
        if flag:
            return origin_img, True

        if min(info['brightness_max']) <= self.threshold and max(info['widths']) > 0:
            # 只断掉了一小截
            indices = np.argmin(info['brightness_max'])
            sample_index = indices // step
            # 画红圈
            cv2.circle(origin_img, (
                offset['x'] + indices,
                offset['y'] + info['first_edge_dis'][sample_index] + info['widths'][sample_index] // 2),
                       30,
                       (0, 0, 255),
                       1)
            flag = True
            # if self.err_choice['断线异常'] == 1:
            return origin_img, True
            # else:
            #     return origin_img, False

        if self.err_choice['边界分岔'] == 1:
            # 是否出现多个线的边界点
            if max(info['edge_counts']) > 2:
                # 画深蓝方框
                cv2.rectangle(origin_img,
                              (offset['x'], offset['y'] + min(info['first_edge_dis']) - 5),
                              (offset['x'] + info['img_width'],
                               offset['y'] + max(info['first_edge_dis']) + max(info['widths']) + 5),
                              (255, 0, 0),
                              1)
                flag = True
                # return origin_img, True

        if self.err_choice['亮度异常'] == 1:
            # 是否亮度异常
            if max(info['brightness_max']) >= brightness_limit:
                indices = np.argmax(info['brightness_max'])
                sample_index = indices // step
                # 画黄圈
                cv2.circle(origin_img, (
                    offset['x'] + indices,
                    offset['y'] + info['first_edge_dis'][sample_index] + info['widths'][sample_index] // 2),
                           30,
                           (0, 255, 255),
                           1)
                flag = True
                # return origin_img, True

        var, mean = self.__compute_var_mean(info['widths'])

        if self.err_choice['过粗过细'] == 1:
            # 是否粗细不合适
            # mean_div_img_width = mean / info['img_width']
            # if self.verbose:
            #     print('mean_div_img_width:{}'.format(mean_div_img_width))
            if mean > width_limit_max or (width_limit_min > mean > 0.0):
                # 画浅蓝方框
                cv2.rectangle(origin_img,
                              (offset['x'], offset['y'] + min(info['first_edge_dis']) - 5),
                              (offset['x'] + info['img_width'],
                               offset['y'] + max(info['first_edge_dis']) + max(info['widths']) + 5),
                              (255, 255, 0),
                              1)
                flag = True
                # return origin_img, True

        if self.err_choice['弯曲异常'] == 1:
            # 是否弯曲太厉害
            max_slope = max(info['slopes'])
            min_slope = min(info['slopes'])
            if max_slope >= slope_limit or abs(min_slope) >= slope_limit:
                # 画紫色方框
                cv2.rectangle(origin_img,
                              (offset['x'], offset['y'] + min(info['first_edge_dis']) - 5),
                              (offset['x'] + info['img_width'],
                               offset['y'] + max(info['first_edge_dis']) + max(info['widths']) + 5),
                              (255, 0, 255),
                              1)
                flag = True
                # return origin_img, True

        if self.err_choice['粗细变化过快'] == 1:
            # 整体粗细变化是否太大,包括方差过大和过多的局部粗细变化
            varys = info['varys']
            if var > var_limit or np.where(np.abs(np.array(varys)) >= 2)[0].shape[0] >= big_vary_count:
                # 画绿框
                cv2.rectangle(origin_img,
                              (offset['x'], offset['y'] + min(info['first_edge_dis']) - 5),
                              (offset['x'] + info['img_width'],
                               offset['y'] + max(info['first_edge_dis']) + max(info['widths']) + 5),
                              (0, 255, 0),
                              1)
                flag = True
                # return origin_img, True

            # 局部粗细变化
            if max(varys) >= variation_limit:
                indexes = [i for i, vary in enumerate(varys) if vary == max(varys)]
                for index in indexes:
                    # 画绿圈
                    index = index + self.sec_size // 2
                    cv2.circle(origin_img,
                               (offset['x'] + index * step,
                                offset['y'] + info['first_edge_dis'][index] + info['widths'][index] // 2),
                               30,
                               (0, 255, 0),
                               1)
                flag = True
                # return origin_img, True
            if abs(min(varys)) >= variation_limit:
                indexes = [i for i, vary in enumerate(varys) if vary == min(varys)]
                for index in indexes:
                    # 画绿圈
                    index = index + self.sec_size // 2
                    cv2.circle(origin_img,
                               (offset['x'] + index * step,
                                offset['y'] + info['first_edge_dis'][index] + info['widths'][index] // 2),
                               30,
                               (0, 255, 0),
                               1)
                flag = True
                # return origin_img, True

        # 非异常的线
        return origin_img, flag

    def __compute_var_mean(self, widths):
        widths = np.array(widths)
        # 计算均值方差
        widths_square = widths * widths
        sum_wid = np.sum(widths)
        sum_wid_square = np.sum(widths_square)
        # print("sum_wid:{}".format(sum_wid))
        # print("sum_wid_square:{}".format(sum_wid_square))
        mean = sum_wid / widths.shape[0]
        var = sum_wid_square / widths.shape[0] - mean ** 2
        if self.verbose:
            print("mean:{}".format(mean))
            print("var:{}".format(var))
        return var, mean

    def __get_brightness(self, gray_img):
        """将灰度图的亮度在竖直方向上做和,返回每一列上亮度的最大值"""
        # brightness_min = np.min(np.where(gray_img >= self.threshold, gray_img, 255), axis=0)
        # cv2.imshow('line', line_img)
        brightness_max = np.max(gray_img, axis=0)
        return brightness_max

    def detect_error_line(self, origin_img, img_name, var_limit=2.0, width_limit_max=11.5, width_limit_min=6.5,
                          slope_limit=5, variation_limit=3, big_vary_count=4, brightness_limit=180):
        """origin_img为RGB图"""
        if self.verbose:
            print('--------------------{}--------------------'.format(img_name))
        gray_img, pre_img = self.__pre_process(origin_img, self.threshold)
        del_img, offset = self.__del_white_margin(pre_img, self.margin)
        # 为灰度图去掉白边
        gray_img = gray_img[offset['y']:offset['y'] + del_img.shape[0], offset['x']:offset['x'] + del_img.shape[1]]

        if self.show:
            cv2.imshow('del_{}'.format(img_name), del_img)

        sample_count = round(del_img.shape[1] / 100 * self.sample_count_per_hundred)
        step = del_img.shape[1] // sample_count
        info = self.__get_info(del_img, gray_img, step)
        detect_img, err_flag = self.__find_error(origin_img, offset, info, step, var_limit, width_limit_max,
                                                 width_limit_min, slope_limit, variation_limit, big_vary_count,
                                                 brightness_limit)
        if self.verbose:
            print('offset:{}'.format(offset))
            print('raw_height:{},raw_width:{}'.format(origin_img.shape[0], origin_img.shape[1]))
            print('del_height:{},del_width:{}'.format(del_img.shape[0], del_img.shape[1]))
        if self.show:
            cv2.imshow('detected_{}'.format(img_name), detect_img)
        return detect_img, err_flag


if __name__ == '__main__':
    detector = LineDetector(verbose=True, show=True, err_choice={'断线异常': 1, '边界分岔': 1, '亮度异常': 1,
                                                                 '弯曲异常': 1, '过粗过细': 1, '粗细变化过快': 1})
    # dir = '20180530-002'
    # names = [
    #     # '153-3.png',
    #     # '154-3.png',
    #     '341-3.jpg',
    #     # '127-3.png',
    #     # '150-2-n.png'
    # ]
    # file_names = os.listdir(dir)
    # detected_dir = os.path.join(dir, 'detected')
    # if not os.path.exists(detected_dir):
    #     os.mkdir(detected_dir)
    #
    # for file_name in file_names:
    #     file_name_with_dir = os.path.join(dir, file_name)
    #     if os.path.isfile(file_name_with_dir):
    #         image = cv2.imread(file_name_with_dir)
    #         detected_img, err = detector.detect_error_line(image, file_name)
    #         if err:
    #             target_file = os.path.join(detected_dir, file_name)
    #             cv2.imwrite(target_file, detected_img)

    file_name = '9.jpg'
    image = cv2.imread(file_name)
    detected_img, err = detector.detect_error_line(image, file_name)
    cv2.waitKey()
    # cv2.waitKey()
