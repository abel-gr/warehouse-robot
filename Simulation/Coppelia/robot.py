import numpy as np
import cv2
from sim import *
from time import sleep
from sympy import *
from sympy.physics.vector import init_vprinting
import math

init_vprinting(use_latex='mathjax', pretty_print=False)
from sympy.physics.mechanics import dynamicsymbols

theta1, theta2, d3, lc, la, lb, theta, alpha, a, d = dynamicsymbols('theta1 theta2 d3 lc la lb theta alpha a d')


class Image:
    def __init__(self, mat, res):
        self.matrix = np.reshape(np.array(mat,dtype=np.uint8), (res[0], res[1], 3))
        self.matrix = cv2.cvtColor(self.matrix, cv2.COLOR_RGB2BGR)
        self.resolution = res
        self.gray = cv2.cvtColor(self.matrix, cv2.COLOR_RGB2GRAY)

    def __getitem__(self, tup):
        return self.matrix[tup[0], tup[1]]


class Sensors:
    def __init__(self, clientID, cam):
        self.clientID = clientID
        self.cam = cam

    def getImage(self):
        retCode, res, image = simxGetVisionSensorImage(self.clientID, self.cam, 0, simx_opmode_oneshot_wait)
        return Image(image, res)


class Legs:
    def __init__(self, clientID, right_wheel, left_wheel):
        self.clientID = clientID
        self.right_wheel = right_wheel
        self.left_wheel = left_wheel

    def forward(self, seconds, speed):
        simxSetJointTargetVelocity(self.clientID, self.right_wheel, speed, simx_opmode_streaming)
        simxSetJointTargetVelocity(self.clientID, self.left_wheel, speed, simx_opmode_streaming)
        sleep(seconds)
        simxSetJointTargetVelocity(self.clientID, self.right_wheel, 0.0, simx_opmode_streaming)
        simxSetJointTargetVelocity(self.clientID, self.left_wheel, 0.0, simx_opmode_streaming)

    pass


class Arm:
    def __init__(self, clientID, base, shoulder, elbow, wrist, arm_tip):
        self.clientID = clientID
        self.base = base
        self.shoulder = shoulder
        self.elbow = elbow
        self.wrist = wrist
        self.tip = arm_tip

    def setEffector(self, val):
        # función que acciona el efector final remotamente
        # val es Int con valor 0 ó 1 para desactivar o activar el actuador final.
        res, retInts, retFloats, retStrings, retBuffer = simxCallScriptFunction(self.clientID,
                                                                                "suctionPad",
                                                                                sim_scripttype_childscript,
                                                                                "setEffector", [val], [], [], "",
                                                                                simx_opmode_blocking)
        return res

    def get_tip(self):
        return simxGetObjectPosition(self.clientID, self.tip, -1, simx_opmode_blocking)

    def move_to(self, coords):
        # Work in progress
        eq1 = 0.17 * cos(theta1) + 0.17 * cos(theta1 + theta2) - coords[0]
        eq2 = 0.17 * sin(theta1) + 0.17 * sin(theta1 + theta2) - coords[1]
        d3 = simxGetObjectPosition(self.clientID, self.shoulder, -1, simx_opmode_blocking)[1][2]
        eq3 = 0.105 - d3 - coords[2]

        precs = [30, 25, 20, 15, 10, 5]
        for p in precs:
            try:
                q = nsolve((eq1, eq2, eq3), (theta1, theta2, d3), (1, 1, 1), prec=p)
            except:
                if p == precs[-1]:
                    print('No se encuentra solución para: ', coords[0], ", ", coords[1], ", ", coords[2])
                    q = [0, 0, 0]

        retCode = simxSetJointTargetPosition(self.clientID, self.base, q[0], simx_opmode_oneshot)
        retCode = simxSetJointTargetPosition(self.clientID, self.shoulder, q[1], simx_opmode_oneshot)
        retCode = simxSetJointTargetPosition(self.clientID, self.elbow, -q[2], simx_opmode_oneshot)
        return retCode

    def direct(self, angles):
        retCode = simxSetJointTargetPosition(self.clientID, self.base, math.radians(angles[0]), simx_opmode_oneshot)
        retCode = simxSetJointTargetPosition(self.clientID, self.shoulder, -math.radians(angles[1]),
                                             simx_opmode_oneshot)
        retCode = simxSetJointTargetPosition(self.clientID, self.elbow, -math.radians(angles[2]), simx_opmode_oneshot)
        retCode = simxSetJointTargetPosition(self.clientID, self.wrist, -math.radians(angles[3]), simx_opmode_oneshot)
        return retCode


class Brain:  # It will be the main class where all the other class will be connected. It will also do all the work
    # related with connecting the code with the simulator
    def __init__(self):
        self.clientID = connect(19999)
        assert self.clientID != -1

        ret_codes = np.zeros(10)
        ret_codes[0], self.obj = simxGetObjectHandle(self.clientID, 'Robot', simx_opmode_blocking)
        ret_codes[1], self.base = simxGetObjectHandle(self.clientID, 'Base_joint', simx_opmode_blocking)
        ret_codes[2], self.shoulder = simxGetObjectHandle(self.clientID, 'Shoulder_joint', simx_opmode_blocking)
        ret_codes[3], self.elbow = simxGetObjectHandle(self.clientID, 'Elbow_joint', simx_opmode_blocking)
        ret_codes[4], self.left_wheel = simxGetObjectHandle(self.clientID, 'Left_wheel_joint', simx_opmode_blocking)
        ret_codes[5], self.right_wheel = simxGetObjectHandle(self.clientID, 'Right_wheel_joint', simx_opmode_blocking)
        ret_codes[6], self.arm_tip = simxGetObjectHandle(self.clientID, 'Arm_tip', simx_opmode_blocking)
        ret_codes[7], self.wrist = simxGetObjectHandle(self.clientID, 'Wrist_joint', simx_opmode_blocking)
        ret_codes[8], self.cam = simxGetObjectHandle(self.clientID, 'Vision_sensor', simx_opmode_blocking)
        ret_codes[9], self.pad = simxGetObjectHandle(self.clientID, 'suctionPad', simx_opmode_blocking)
        assert not all(ret_codes)

        self.arm = Arm(self.clientID, self.base, self.shoulder, self.elbow, self.wrist, self.arm_tip)
        self.legs = Legs(self.clientID, self.left_wheel, self.right_wheel)
        self.sensors = Sensors(self.clientID, self.cam)

        print("Initialization completed, connection established")


"""
Ideas que tengo:

1. Legs Que el brain pueda llamar a una funcion "move" i le passe por parametro un vector 2d representando el vector 
de movimiento que tiene que seguir el robot. Internamente esta funcion tratara con el objeto Legs que sera el 
encargado de mover los joints de las ruedas a la velocidad adecuada para que el robot siga el vector especificado 

2.Image, usar esta classe como si fuera una matriz numpy (internamente lo es). Para eso he creado el operador "[ ]", 
de forma que podamos acceder a la matriz del objeto de manera fàcil. La idea és implementar funciones de Vision por 
Computador dentro de la classe. Por ejemplo una funcion "Detect" que ejecute algun algoritmo de segmentación que 
detecte si hay cajas en la imagen, si hay la línea del suelo que haya que seguir etc. 

"""
