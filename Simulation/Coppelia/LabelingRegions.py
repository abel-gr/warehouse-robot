import numpy as np
import cv2


def LabelingRegions(img):
    K = 1
    im_out = np.zeros((img.shape), dtype=np.uint8)

    equivalences = {}

    # Iterate over image to set labels
    for i, r in enumerate(img):
        for j, p in enumerate(r):
            if (p != 0):
                Xu = i - 1
                Xl = j - 1

                if (Xu >= 0 and Xl >= 0):

                    im_out_xu = im_out[Xu, j]
                    im_out_xl = im_out[i, Xl]

                    if (im_out_xu != 0 and im_out_xl == 0):
                        im_out[i, j] = im_out_xu

                    elif (im_out_xu == 0 and im_out_xl != 0):
                        im_out[i, j] = im_out_xl

                    elif (im_out_xu != 0 and im_out_xl != 0):
                        im_out[i, j] = im_out_xl

                        if (im_out_xu != im_out_xl):
                            if im_out_xl in equivalences:
                                if im_out_xu not in equivalences[im_out_xl]:
                                    equivalences[im_out_xl].append(im_out_xu)
                            else:
                                equivalences[im_out_xl] = [im_out_xu]

                    elif (im_out_xu == 0 and im_out_xl == 0):
                        im_out[i, j] = K
                        K = K + 1

    # Replace the labels of the dictionary of equivalences.
    for k, v in equivalences.items():
        for equiv in v:
            im_out[im_out == equiv] = k

    return im_out


def LabelingRegionsC8(img):

    K = 1
    im_out = np.zeros((img.shape), dtype=np.uint8)

    equivalences = {}

    # Iterate over image to set labels
    for i, r in enumerate(img):
        for j, p in enumerate(r):
            if (p != 0):
                Xu = i - 1
                Xl = j - 1
                Xr = j + 1

                if (Xu >= 0 and Xl >= 0 and Xr < im_out.shape[1]):

                    im_out_xu = im_out[Xu, j]
                    im_out_xl = im_out[i, Xl]
                    im_out_xul = im_out[Xu, Xl]
                    im_out_xur = im_out[Xu, Xr]

                    if (im_out_xu != 0 and im_out_xul == 0 and im_out_xl == 0 and im_out_xur == 0):
                        im_out[i, j] = im_out_xu

                    elif (im_out_xu == 0 and im_out_xul != 0 and im_out_xl == 0 and im_out_xur == 0):
                        im_out[i, j] = im_out_xul

                    elif (im_out_xu == 0 and im_out_xul == 0 and im_out_xl != 0 and im_out_xur == 0):
                        im_out[i, j] = im_out_xl

                    elif (im_out_xu == 0 and im_out_xul == 0 and im_out_xl == 0 and im_out_xur != 0):
                        im_out[i, j] = im_out_xur

                    elif (im_out_xu != 0 and im_out_xul == 0 and im_out_xl != 0 and im_out_xur == 0):
                        im_out[i, j] = im_out_xl

                        if (im_out_xu != im_out_xl):
                            if im_out_xu in equivalences:
                                if im_out_xl not in equivalences[im_out_xu]:
                                    equivalences[im_out_xu].append(im_out_xl)
                            else:
                                equivalences[im_out_xu] = [im_out_xl]

                    elif (im_out_xu == 0 and im_out_xul != 0 and im_out_xl != 0 and im_out_xur == 0):
                        im_out[i, j] = im_out_xl

                        if (im_out_xul != im_out_xl):
                            if im_out_xul in equivalences:
                                if im_out_xl not in equivalences[im_out_xul]:
                                    equivalences[im_out_xul].append(im_out_xl)
                            else:
                                equivalences[im_out_xul] = [im_out_xl]

                    elif (im_out_xu != 0 and im_out_xul != 0 and im_out_xl == 0 and im_out_xur == 0):
                        im_out[i, j] = im_out_xul

                        if (im_out_xu != im_out_xul):
                            if im_out_xu in equivalences:
                                if im_out_xul not in equivalences[im_out_xu]:
                                    equivalences[im_out_xu].append(im_out_xul)
                            else:
                                equivalences[im_out_xu] = [im_out_xul]


                    elif (im_out_xu != 0 and im_out_xul == 0 and im_out_xl == 0 and im_out_xur != 0):
                        im_out[i, j] = im_out_xu

                        if (im_out_xur != im_out_xu):
                            if im_out_xur in equivalences:
                                if im_out_xu not in equivalences[im_out_xur]:
                                    equivalences[im_out_xur].append(im_out_xu)
                            else:
                                equivalences[im_out_xur] = [im_out_xu]

                    elif (im_out_xu == 0 and im_out_xul != 0 and im_out_xl == 0 and im_out_xur != 0):
                        im_out[i, j] = im_out_xul

                        if (im_out_xur != im_out_xul):
                            if im_out_xur in equivalences:
                                if im_out_xul not in equivalences[im_out_xur]:
                                    equivalences[im_out_xur].append(im_out_xul)
                            else:
                                equivalences[im_out_xur] = [im_out_xul]

                    elif (im_out_xu == 0 and im_out_xul == 0 and im_out_xl != 0 and im_out_xur != 0):
                        im_out[i, j] = im_out_xl

                        if (im_out_xur != im_out_xl):
                            if im_out_xur in equivalences:
                                if im_out_xl not in equivalences[im_out_xur]:
                                    equivalences[im_out_xur].append(im_out_xl)
                            else:
                                equivalences[im_out_xur] = [im_out_xl]

                    elif (im_out_xu == 0 and im_out_xul == 0 and im_out_xl == 0 and im_out_xur == 0):
                        im_out[i, j] = K
                        K = K + 1

                    else:

                        if (im_out_xl != 0):
                            save = im_out_xl
                        else:
                            save = im_out_xul

                        im_out[i, j] = save

                        if (im_out_xu != save and im_out_xu != 0):
                            if im_out_xu in equivalences:
                                if save not in equivalences[im_out_xu]:
                                    equivalences[im_out_xu].append(save)
                            else:
                                equivalences[im_out_xu] = [save]

                        if (im_out_xul != save and im_out_xul != 0):
                            if im_out_xul in equivalences:
                                if save not in equivalences[im_out_xul]:
                                    equivalences[im_out_xul].append(save)
                            else:
                                equivalences[im_out_xul] = [save]

                        if (im_out_xur != save and im_out_xur != 0):
                            if im_out_xur in equivalences:
                                if save not in equivalences[im_out_xur]:
                                    equivalences[im_out_xur].append(save)
                            else:
                                equivalences[im_out_xur] = [save]

                        if (im_out_xl != save and im_out_xl != 0):
                            if im_out_xl in equivalences:
                                if save not in equivalences[im_out_xl]:
                                    equivalences[im_out_xl].append(save)
                            else:
                                equivalences[im_out_xl] = [save]

                                # Replace the labels of the dictionary of equivalences.
    for k, v in equivalences.items():
        for equiv in v:
            if (k in equivalences):
                im_out[im_out == k] = equiv

    return [im_out, equivalences]
