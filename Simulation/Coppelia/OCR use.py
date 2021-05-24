# -*- coding: utf-8 -*-

from PIL import Image
import numpy as np
import LettersNumbersClassification as LetNumClassif
import OCR_Lite as OCR
import matplotlib.pyplot as plt
import cv2

# Train the MLP (only need to do it once as it saves the model in a file, so now it is commented)
LetNumClassif.train('dataset/fonts')

img = Image.open('dataset/labels/numbers4.png')
img = np.asarray(img, dtype=np.float32)
img = np.mean(img, axis=2)
img = np.where(img > 150, 0, 1)

plt.figure(figsize=(9, 5))
plt.imshow(img, cmap='gray', vmin=0, vmax=1)
plt.show()

text = OCR.OCR(img)
print(text)
