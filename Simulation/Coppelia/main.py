from robot import Brain
from matplotlib import pyplot as plt
import math
import time
b = Brain()

b.arm.move_to([0, -1.23, 0.25])
#b.legs.forward(3, 0.6)