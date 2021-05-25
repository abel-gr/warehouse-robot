# -*- coding: utf-8 -*-

import LabelingRegions as LabelingRegions
import LettersNumbersClassification as LetNumClassif
import cv2
import numpy as np
import matplotlib.pyplot as plt
from textblob import TextBlob
import math
from scipy import ndimage


def classifyImages(imgs):
    return LetNumClassif.ClassifyLettersNumbers(imgs)


def segmentRegions(im, labels):
    current_meanY = -1
    row = 1

    minquantity = LetNumClassif.dataset_images_sizeX * 0.4

    labeled_letters = []
    for region_number, quantity in labels:
        if region_number != 0:
            if quantity > minquantity:
                letter = np.where(im == region_number, 1, 0)

                s0 = letter.shape[0]
                s1 = letter.shape[1]

                indices = np.where(letter == 1)

                y0 = np.min(indices[0]) - 5
                y1 = np.max(indices[0]) + 5
                x0 = np.min(indices[1]) - 5
                x1 = np.max(indices[1]) + 5

                if (y0 < 0):
                    y0 = 0

                if (y1 >= s0):
                    y1 = s0 - 1

                if (x0 < 0):
                    x0 = 0

                if (x1 >= s1):
                    x1 = s1 - 1

                letter = letter[y0:y1, x0:x1]

                # mean value x and y for sorting
                in_m0 = int(indices[0].shape[0] / 2)
                in_m1 = int(indices[1].shape[0] / 2)
                meanval0 = np.mean(indices[0])
                meanval1 = np.mean(indices[1])

                if (current_meanY == -1):
                    current_meanY = meanval0

                if (meanval0 - current_meanY > ((y1 - y0) * 0.5)):
                    current_meanY = meanval0
                    row = row + 1

                labeled_letters.append([letter, row, meanval1])

    labeled_letters_sorted = sorted(labeled_letters, key=lambda v: (v[1], v[2]))

    return labeled_letters_sorted


def labelingRegions(img):

    [im_out, eq] = LabelingRegions.LabelingRegionsC8(img)

    unique, counts = np.unique(im_out.reshape(-1), return_counts=True)
    labels = np.asarray((unique, counts)).T

    return [im_out, labels]


"""
OCR main function. If it found text in the image, it returns it as string.

input:
    - im: The image that want to recognize the text

output:
    - text: The text found in the image as string
"""


def OCR(im):

    [im, labels] = labelingRegions(im)

    letters = segmentRegions(im, labels)

    text = classifyImages(letters)
    lines = text.split('\n')

    corrected_lines = []
    for i in lines:
        corrected_lines.append(TextBlob(i))

    correct_text = ""
    for i in corrected_lines:
        correct_text += str(i.correct()) + '\n'

    return text


def sort_ar(ar):
    return ar.shape[0]


def reorientation(im):  # Hecha por Arnau Mayoral 1528912
    kernel = np.ones((6, 6), 'uint8')
    # res = np.pad(res, 20)

    img_edges = cv2.dilate(im, kernel, iterations=20)
    img_edges = cv2.Canny(img_edges, 0, 255, apertureSize=3)
    img_edges = cv2.dilate(img_edges, np.ones((2, 2), 'uint8'), iterations=20)

    lines = cv2.HoughLinesP(img_edges, 1, math.pi / 180.0, 100, minLineLength=100, maxLineGap=5)

    angles = []

    if not hasattr(lines, '__len__'):
        return im
    for [[x1, y1, x2, y2]] in lines:
        # cv2.line(res, (x1, y1), (x2, y2), (255, 0, 0), 3)
        angle = math.degrees(math.atan2(y2 - y1, x2 - x1))
        if abs(angle) < 10:
            angles.append(angle)

    median_angle = np.mean(angles)
    img_rotated = ndimage.rotate(im, median_angle)
    return img_rotated


def segment(im):  # Hecha por Arnau Mayoral 1528912

    im = np.where(im > 50, 0, 1)
    im = im.astype('uint8')
    im = im * 255

    kernel = np.ones((5, 5), 'uint8')

    dil = cv2.dilate(im, kernel, iterations=15)
    can = cv2.Canny(dil, 0, 255)
    can = cv2.dilate(can, kernel, iterations=1)

    contours, hierarchy = cv2.findContours(can, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    contours = sorted(contours, key=sort_ar)

    if len(contours) == 0:
        return -1

    txt = contours[0]

    x, y, w, h = cv2.boundingRect(txt)

    res = np.zeros((h, w), dtype='uint8')
    for i in range(h):
        for j in range(w):
            res[i, j] = im[y + i, x + j]

    img_rotated = reorientation(res)

    img_rotated = np.pad(img_rotated, 50)

    img_rotated = np.where(img_rotated < 50, 0, 1)
    img_rotated = img_rotated*255
    img_rotated = img_rotated.astype('float32')
    return img_rotated
