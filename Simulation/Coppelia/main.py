from robot import Brain
from matplotlib import pyplot as plt
import math
b = Brain()

b.arm.direct((180, 0, 0, 0))

img = b.sensors.getImage()
plt.figure(1)
plt.imshow(img.matrix)
plt.show()

#b.legs.forward(3, 5.6)