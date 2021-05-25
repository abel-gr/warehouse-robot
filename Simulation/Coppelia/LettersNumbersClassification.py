import numpy as np
from joblib import load, dump
from PIL import Image

import os

from sklearn.neural_network import MLPClassifier
from sklearn.model_selection import train_test_split
from sklearn.utils import shuffle

import matplotlib.pyplot as plt


def getClassIDfromChar(character, CaseSensitive=False):
    code = ord(character)

    if (code > 64 and code < 91):
        code = code - 7

    elif (code > 96 and code < 123):
        if (CaseSensitive):
            code = code - 13
        else:
            code = code - 39

    code = code - 48

    if (code == 183):
        if (CaseSensitive):
            code = 62
        else:
            code = 36
    elif (code == 151):
        if (CaseSensitive):
            code = 63
        else:
            code = 36
    elif (code == 193):
        if (CaseSensitive):
            code = 64
        else:
            code = 37
    elif (code == 161):
        if (CaseSensitive):
            code = 65
        else:
            code = 37

    return code


def getCharFromClassID(code, CaseSensitive=False):
    if (CaseSensitive):

        if (code == 62):
            return 'ç'
        elif (code == 63):
            return 'Ç'
        elif (code == 64):
            return 'ñ'
        elif (code == 65):
            return 'Ñ'

    else:

        if (code == 36):
            return 'Ç'
        elif (code == 37):
            return 'Ñ'

    code = code + 48

    if (code > 57 and code < 84):
        code = code + 7

    elif (code > 83 and code < 110):
        if (CaseSensitive):
            code = code + 13
        else:
            code = code + 39

    return chr(code[0])


dataset_images_sizeX = 100
dataset_images_sizeY = 150

imScales = [0.3, 0.4, 0.5, 0.6, 0.7, 1.0]


def train(imgs_path):
    dicClases = {}

    X = []
    y = []

    for i in range(1, 6):
        path = imgs_path + '/font' + str(i) + '/'

        for x in os.listdir(path):

            for j in imScales:
                img = Image.open(path + x)

                s0 = (int)(dataset_images_sizeX * j)
                s1 = (int)(dataset_images_sizeY * j)

                img = img.resize((s0, s1))
                img = np.asarray(img, dtype=np.float32)
                img = np.mean(img, axis=2)
                img = np.where(img < 200, 1, 0)

                indices = np.where(img == 1)

                y0 = np.min(indices[0]) - 5
                y1 = np.max(indices[0]) + 5
                x0 = np.min(indices[1]) - 5
                x1 = np.max(indices[1]) + 5

                if (y0 < 0):
                    y0 = 0

                if (y1 >= s1):
                    y1 = s1 - 1

                if (x0 < 0):
                    x0 = 0

                if (x1 >= s0):
                    x1 = s0 - 1

                img = img[y0:y1, x0:x1]

                img = Image.fromarray(img)
                img = np.asarray(img.resize((dataset_images_sizeX, dataset_images_sizeY)))

                clase = getClassIDfromChar(x[0], False)

                """
                lett = getCharFromClassID(clase)
                plt.figure(figsize=(9,5))
                plt.imshow(img, cmap='gray', vmin=0, vmax=1)
                plt.title(str(clase) + ", " + str(lett))
                plt.show()
                """

                X.append(img.reshape(-1))
                y.append(clase)

            if (clase not in dicClases):
                dicClases[clase] = x[0]

    X = np.asarray(X)
    TY = np.asarray(y)

    y = np.zeros((TY.shape[0], len(dicClases.keys()) + 1), np.uint8)

    for i, tyVal in enumerate(TY):
        y[i, tyVal] = 1

    X, y = shuffle(X, y, random_state=0)

    X_train, X_test, y_train, y_test = train_test_split(X, y, train_size=0.8, stratify=y, random_state=1)

    clf = MLPClassifier(random_state=1, max_iter=2000, hidden_layer_sizes=[400, 200, 200],
                        learning_rate_init=1.0e-3, alpha=0.01)

    clf.fit(X_train, y_train)

    dump(clf, 'MLP.joblib')


def ClassifyLettersNumbers(imgs):
    clf = load('MLP.joblib')

    ln = ''

    crow = 1
    prevMeanVal1 = 0

    for im, row, meanval1 in imgs:

        im_c = Image.fromarray(im)
        im_c = np.asarray(im_c.resize((dataset_images_sizeX, dataset_images_sizeY)))
        im_c = np.where(im_c == 1, 1, 0)

        y_pred = clf.predict_proba(im_c.reshape(1, -1))

        clase = y_pred.argmax(axis=1)

        lett = getCharFromClassID(clase)

        """
        plt.figure(figsize=(9,5))
        plt.imshow(im_c, cmap='gray', vmin=0, vmax=1)
        plt.title(lett)
        plt.show()
        """

        if (row != crow):

            ln = ln + '\n'
            crow = row
            prevMeanVal1 = 0

        else:

            if (meanval1 - prevMeanVal1) > (dataset_images_sizeX * 0.35):
                ln = ln + ' '

        prevMeanVal1 = meanval1

        ln = ln + lett

        # print(lett, row, meanval1)

    return ln
