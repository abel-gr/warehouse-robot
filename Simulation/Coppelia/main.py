from robot import Brain

# DEMO SIMULATION CODE
# Respresenting a the command {TAKE 5241730 & 0530260 DELIVER TO DROP_ZONE_A, DROP_ZONE_B}
# We know from our database that:
# 5241730 is found in [-0.55, -4.35, 0.05]
# 0530260 is found in [0.25, -4.35, 0.05]
# DROP_ZONE_A is at [-0.45, 2.45, 0.35]
# DROP_ZONE_B is at [-0.123, 2.45, 0.35]

b = Brain()

b.go_to([-0.55, -4.35, 0.05])
b.save_package([-0.55, -4.35, 0.05], 1)
b.go_to([0.25, -4.35, 0.05])
b.save_package([0.25, -4.35, 0.05], 2)

b.go_to([-0.45, 2.1, 0.05])
b.drop_package([-0.45, 2.45, 0.35], 1)
b.drop_package([-0.123, 2.45, 0.35], 2)

