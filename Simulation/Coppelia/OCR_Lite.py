# -*- coding: utf-8 -*-

import LabelingRegions as LabelingRegions
import LettersNumbersClassification as LetNumClassif

import numpy as np


def classifyImages(imgs):
    return LetNumClassif.ClassifyLettersNumbers(imgs)


def segmentRegions(im, labels):
    current_meanY = -1
    row = 1
    
    minquantity = LetNumClassif.dataset_images_sizeX * 0.4

    labeled_letters = []
    for region_number, quantity in labels:
        if(region_number!=0):
            if(quantity > minquantity):
                letter = np.where(im==region_number, 1, 0)
                
                s0 = letter.shape[0]
                s1 = letter.shape[1]
                
                indices = np.where(letter==1)

                y0 = np.min(indices[0]) - 5
                y1 = np.max(indices[0]) + 5
                x0 = np.min(indices[1]) - 5
                x1 = np.max(indices[1]) + 5
                
                
                if(y0 < 0):
                    y0 = 0
                
                if(y1 >= s0):
                    y1 = s0 - 1
                    
                if(x0 < 0):
                    x0 = 0
                    
                if(x1 >= s1):
                    x1 = s1 - 1
                
                letter = letter[y0:y1, x0:x1]
                
                # mean value x and y for sorting
                in_m0 = int(indices[0].shape[0] / 2)
                in_m1 = int(indices[1].shape[0] / 2)
                meanval0 = np.mean(indices[0])
                meanval1 = np.mean(indices[1])
                

                if (current_meanY == -1):
                    current_meanY = meanval0

                if (meanval0 - current_meanY >  ((y1-y0) * 0.5)):
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
    
    return text






