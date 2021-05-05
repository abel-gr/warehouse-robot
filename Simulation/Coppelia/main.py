from robot import Brain
from matplotlib import pyplot as plt
import math
from time import sleep
b = Brain()

while True:
    b.legs.forward(10)
    sleep(5)
    b.check()
    b.legs.forward(10)
    sleep(5)
    b.turn_right()

#b.legs.forward(3, 0.6)