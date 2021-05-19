from robot import Brain
from matplotlib import pyplot as plt
import math
from time import sleep

b = Brain()
# b.turn_right()
# b.arm.direct([-90, 90, 0], unit='deg')

b.take_package([-0.275, -0.1, 0.237])
b.drop_package()
b.legs.forward(3)
"""
sleep(2)

im = b.sensors.getImage()
plt.figure(1)
plt.imshow(im.matrix)
plt.show()
"""
