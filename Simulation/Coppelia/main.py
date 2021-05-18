from robot import Brain
from matplotlib import pyplot as plt
import math
from time import sleep

b = Brain()
# b.turn_right()
# b.arm.direct([-90, 90, 0], unit='deg')
""""""
b.arm.move_to([-0.325, -0.1, 0.2])  # esquerra

sleep(2)
b.arm.setEffector(1)
b.arm.direct([-90, 31, 128], unit='deg')


