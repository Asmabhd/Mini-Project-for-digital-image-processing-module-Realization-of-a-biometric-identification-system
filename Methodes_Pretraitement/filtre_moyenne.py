# -*- coding: utf-8 -*-
"""
Created on Sun Mar 28 22:20:15 2021

@author: pc
"""

import numpy as np
import cv2 as cv
import math


def calculate_template_space(temp_side_length):
        return int(temp_side_length/2)


def median_filter(image, template_side_length):
    new_image = np.zeros(image.shape, image.dtype)
    template_space = calculate_template_space(template_side_length)
    template = []
    half_template = int((template_side_length-1)/2)

    for x in range(template_space, new_image.shape[1] - template_space):
        a = x + half_template
        for y in range(template_space, new_image.shape[0] - template_space):
            b = y + half_template
            for c in range(0, template_side_length):
                for d in range(0, template_side_length):
                    template.append(image[b - d, a - c])
            template.sort()
            new_image[y, x] = template[int((int(math.pow(template_side_length, 2)) - 1) / 2)]
            template = []
    return new_image

img = cv.imread("001_1_1.bmp", cv.IMREAD_GRAYSCALE)
filter_size = 9
new_img = median_filter(img, filter_size)
cv.imwrite("filtre_moyenne" + str(filter_size) + "_.bmp", new_img)
cv.waitKey(0)
cv.destroyAllWindows()
