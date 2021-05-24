from robot import Brain

import math
from time import sleep


b = Brain()

b.go_to([-0.55, -4.35, 0.05])

b.save_package([-0.55, -4.35, 0.05], 1)

b.save_package([0.25, -4.35, 0.05], 2)

b.go_to([-0.27, 2.1, 0.05])
b.drop_package([-0.45, 2.45, 0.35], 1)
b.drop_package([-0.123, 2.45, 0.35], 2)

