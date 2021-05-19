import numpy as np
import cv2
from sim import *
from time import sleep
from sympy import sin, cos, nsolve
from sympy.physics.vector import init_vprinting
from math import pi, floor, ceil, radians, degrees, atan2, acos, sqrt
import math
import vg
from random import randint

init_vprinting(use_latex='mathjax', pretty_print=False)
from sympy.physics.mechanics import dynamicsymbols

theta1, theta2, theta3, theta4, d3, lc, la, lb, alpha, a, d = dynamicsymbols(
    'theta1 theta2 theta3 theta4 d3 lc la lb alpha a d')


class Image:
    def __init__(self, mat, res):
        self.matrix = np.reshape(np.array(mat, dtype=np.uint8), (res[0], res[1], 3))
        self.matrix = cv2.cvtColor(self.matrix, cv2.COLOR_RGB2BGR)
        self.resolution = res
        self.gray = cv2.cvtColor(self.matrix, cv2.COLOR_RGB2GRAY)

    def __getitem__(self, tup):
        return self.matrix[tup[0], tup[1]]


class Sensors:
    def __init__(self, clientID, cam, psensor, body, sensor_left, sensor_right):
        self.clientID = clientID
        self.cam = cam
        self.psensor = psensor
        self.body = body
        self.sensorl = sensor_left
        self.sensorr = sensor_right

        print(psensor)

    def getImage(self):
        retCode, res, image = simxGetVisionSensorImage(self.clientID, self.cam, 0, simx_opmode_oneshot_wait)
        return Image(image, res)

    def getDistance(self, t_sensor):
        retCode, detectionState, detectedPoint, detectedObjectHandle, detectedSurfaceNormalVector = simxReadProximitySensor(
            self.clientID, t_sensor, simx_opmode_blocking)
        print(retCode)
        sensor_val = -1
        if detectionState == True:
            sensor_val = np.linalg.norm(detectedPoint)
            print("distacia al objeto: ", sensor_val)
        else:
            print("No ha detectado objeto")
        return sensor_val

    def yaw(self):
        ret, bd = simxGetObjectOrientation(self.clientID, self.body, -1, simx_opmode_blocking)
        # print(np.rad2deg(bd[2]))
        return np.rad2deg(bd[2])


class Legs:
    def __init__(self, clientID, right_wheel, left_wheel):
        self.clientID = clientID
        self.right_wheel = right_wheel
        self.left_wheel = left_wheel

        ret_codes = np.zeros(13)
        ret_codes[0], self.obj = simxGetObjectHandle(self.clientID, 'Robot', simx_opmode_blocking)
        ret_codes[1], self.cam = simxGetObjectHandle(self.clientID, 'Vision_sensor', simx_opmode_blocking)
        ret_codes[2], self.psensor = simxGetObjectHandle(self.clientID, 'Psensor', simx_opmode_blocking)
        ret_codes[3], self.bdummy = simxGetObjectHandle(self.clientID, 'Back_dummy', simx_opmode_blocking)
        ret_codes[4], self.fdummy = simxGetObjectHandle(self.clientID, 'Front_dummy', simx_opmode_blocking)
        ret_codes[5], self.sensor_left = simxGetObjectHandle(self.clientID, 'sensor_left', simx_opmode_blocking)
        ret_codes[6], self.sensor_right = simxGetObjectHandle(self.clientID, 'sensor_right', simx_opmode_blocking)

        assert not all(ret_codes)

        self.sensors = Sensors(self.clientID, self.cam, self.psensor, self.bdummy, self.fdummy, self.obj)

    def forward(self, speed, b):
        op = 1
        simxSetJointTargetVelocity(self.clientID, self.left_wheel, speed, simx_opmode_streaming)
        simxSetJointTargetVelocity(self.clientID, self.right_wheel, speed, simx_opmode_streaming)
        b.distance_side()
        b.check_proximity(op)

    def forward(self, speed):
        simxSetJointTargetVelocity(self.clientID, self.left_wheel, speed, simx_opmode_streaming)
        simxSetJointTargetVelocity(self.clientID, self.right_wheel, speed, simx_opmode_streaming)

    def turn_left(self, speed, required, b):
        distance = self.sensors.getDistance(self.psensor)
        while (distance > 0.7 or distance == -1 or required):
            distance = self.sensors.getDistance(self.psensor)
            ret = simxSetJointTargetVelocity(self.clientID, self.left_wheel, speed, simx_opmode_streaming)
            ret = simxSetJointTargetVelocity(self.clientID, self.right_wheel, -speed, simx_opmode_streaming)
            if required:
                sleep(1)
            required = False
            sleep(0.3)
            b.check_proximity(1)

    def turn_right(self, speed, required, b):
        distance = self.sensors.getDistance(self.psensor)
        while (distance > 0.7 or distance == -1 or required):
            distance = self.sensors.getDistance(self.psensor)
            ret = simxSetJointTargetVelocity(self.clientID, self.left_wheel, -speed, simx_opmode_streaming)
            ret = simxSetJointTargetVelocity(self.clientID, self.right_wheel, speed, simx_opmode_streaming)
            if required:
                sleep(1)
            required = False
            sleep(0.3)
            b.check_proximity(2)

    def stop(self):
        simxSetJointTargetVelocity(self.clientID, self.left_wheel, 0.0, simx_opmode_streaming)
        simxSetJointTargetVelocity(self.clientID, self.right_wheel, 0.0, simx_opmode_streaming)

    pass


class Arm:
    def __init__(self, clientID, base, shoulder, elbow, wrist, arm_tip):
        self.clientID = clientID
        self.base = base
        self.shoulder = shoulder
        self.elbow = elbow
        self.wrist = wrist
        self.tip = arm_tip
        self.angles = [-90, -60, -130, -100]

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

    def first_quadrant(self, n):

        if 0 > n > -90:
            n = n * -1
        if -90 > n > -180:
            n = 180 + n
        if 180 < n < 270:
            n = n - 180
        if 270 < n < 360:
            n = n - 180

        return n

    def move_to(self, coords):
        """
        l1 = 0.2659
        l2 = 0.2585
        l3 = 0.1415
        l4 = 0.0750
        """
        p = simxGetObjectPosition(self.clientID, self.base, -1, simx_opmode_blocking)[1]
        H = 265.9
        b = 258.5
        ab = 141.5
        m = 75

        x = (coords[0] - p[0]) * 1000
        y = (coords[1] - p[1]) * 1000
        z = (coords[2]) * 1000
        cabGrados = 0
        Axis5 = 90  # giro de la pinza es directo
        Pinza = 110
        cabRAD = cabGrados * pi / 180  # angulo cabeceo en rad.
        Axis1 = atan2(y, x)
        M = sqrt(pow(x, 2) + pow(y, 2))
        xprima = M
        yprima = z
        Afx = cos(cabRAD) * m
        B = xprima - Afx
        Afy = sin(cabRAD) * m
        A = yprima + Afy - H
        Hip = sqrt(pow(A, 2) + pow(B, 2))
        alfa = atan2(A, B)
        beta = acos((pow(b, 2) - pow(ab, 2) + pow(Hip, 2)) / (2 * b * Hip))
        Axis2 = alfa + beta
        gamma = acos((pow(b, 2) + pow(ab, 2) - pow(Hip, 2)) / (2 * b * ab))
        Axis3 = gamma
        Axis4 = 2 * pi - cabRAD - Axis2 - Axis3
        Axis1Grados = Axis1 * 180 / pi  # Giro base en Grados
        Axis2Grados = 90 - Axis2 * 180 / pi  # Giro brazo en Grados
        Axis3Grados = 180 - Axis3 * 180 / pi  # Giro antebrazo grados
        Axis4Grados = 0  # Giro muñequilla grados

        print(Axis1Grados, Axis2Grados, Axis3Grados, Axis4Grados)
        self.confort()
        self.direct([Axis1Grados, Axis2Grados, Axis3Grados, 60], unit='deg')
        o = simxGetObjectOrientation(self.clientID, self.wrist, self.base, simx_opmode_blocking)[1]
        o = np.array(o)
        print(degrees(o[0]), degrees(o[1]), degrees(o[2]))
        t = (90 + degrees(o[2])) - (self.angles[3] * (-1))
        self.direct([Axis1Grados, Axis2Grados, Axis3Grados, -t], unit='deg')

    def direct(self, angles, unit='rad'):
        if unit == 'rad':
            if len(angles) > 3:
                retCode = simxSetJointTargetPosition(self.clientID, self.wrist, -angles[3], simx_opmode_oneshot)
                self.angles[3] = degrees(angles[3])
            retCode = simxSetJointTargetPosition(self.clientID, self.base, angles[0] + pi, simx_opmode_oneshot)
            self.angles[0] = degrees(angles[0] + pi)
            sleep(1)
            retCode = simxSetJointTargetPosition(self.clientID, self.shoulder, angles[1],
                                                 simx_opmode_oneshot)
            self.angles[1] = degrees(angles[1])
            sleep(1)
            retCode = simxSetJointTargetPosition(self.clientID, self.elbow, angles[2], simx_opmode_oneshot)
            self.angles[2] = degrees(angles[2])
            sleep(1)

        else:
            if len(angles) > 3:
                retCode = simxSetJointTargetPosition(self.clientID, self.wrist, -radians(angles[3]),
                                                     simx_opmode_oneshot)
                self.angles[3] = angles[3]
            retCode = simxSetJointTargetPosition(self.clientID, self.base, radians(angles[0]) + pi, simx_opmode_oneshot)
            sleep(1)
            retCode = simxSetJointTargetPosition(self.clientID, self.shoulder, radians(angles[1]),
                                                 simx_opmode_oneshot)
            sleep(1)
            retCode = simxSetJointTargetPosition(self.clientID, self.elbow, radians(angles[2]),
                                                 simx_opmode_oneshot)
            sleep(1)
            self.angles[0] = angles[0]
            self.angles[1] = angles[1]
            self.angles[2] = angles[2]

        return retCode

    def confort(self):
        self.direct([self.angles[0], 55, 130, self.angles[3]], unit='deg')

    def forward(self):
        self.direct([self.angles[0], 0, 0, self.angles[3]], unit='deg')
        self.direct([-90, -60, -130, -100], unit='deg')


class Brain:  # It will be the main class where all the other class will be connected. It will also do all the work
    # related with connecting the code with the simulator
    def __init__(self):
        self.corr = 0
        self.clientID = connect(19999)
        assert self.clientID != -1
        self.axis = np.array([0, 0, 0])
        self.arm_home = [-90, 90, 0]
        ret_codes = np.zeros(14)
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
        ret_codes[10], self.psensor = simxGetObjectHandle(self.clientID, 'Psensor', simx_opmode_blocking)
        ret_codes[11], self.backpack = simxGetObjectHandle(self.clientID, 'Backpack', simx_opmode_blocking)
        ret_codes[12], self.sensor_left = simxGetObjectHandle(self.clientID, 'sensor_left', simx_opmode_blocking)
        ret_codes[13], self.sensor_right = simxGetObjectHandle(self.clientID, 'sensor_right', simx_opmode_blocking)

        assert not all(ret_codes)

        self.arm = Arm(self.clientID, self.base, self.shoulder, self.elbow, self.wrist, self.arm_tip)
        self.legs = Legs(self.clientID, self.left_wheel, self.right_wheel)
        self.sensors = Sensors(self.clientID, self.cam, self.psensor, self.obj, self.sensor_left, self.sensor_right)
        self.sensorl = Sensors(self.clientID, self.cam, self.sensor_left, self.obj, self.sensor_left, self.sensor_right)
        self.sensorr = Sensors(self.clientID, self.cam, self.sensor_right, self.obj, self.sensor_left,
                               self.sensor_right)

        print("Initialization completed, connection established")

    def turn_left(self):
        self.check()
        self.legs.turn_left(1, False)
        deg = self.sensors.yaw()
        stop = 88
        if deg < 0 and self.axis[2] == 180:
            r = deg < self.axis[2] * -1 + stop
        elif deg > 0 and self.axis[2] == -180:
            r = deg < self.axis[2] * -1 + stop
        else:
            r = deg < self.axis[2] + stop
        while r:
            deg = self.sensors.yaw()
            if deg < 0 and self.axis[2] == 180:
                r = deg < self.axis[2] * -1 + stop
            elif deg > 0 and self.axis[2] == -180:
                r = deg < self.axis[2] * -1 + stop
            else:
                r = deg < self.axis[2] + stop

        self.legs.stop()
        if self.axis[2] == 180:
            self.axis[2] = -180
        self.axis[2] += 90
        self.check()
        sleep(0.5)
        # self.check()

    def turn_right(self):
        self.check()
        self.legs.turn_right(1, False)
        deg = self.sensors.yaw()
        stop = 88
        if deg < 0 and self.axis[2] == 180:
            r = deg > self.axis[2] * -1 - stop
        elif deg > 0 and self.axis[2] == -180:
            r = deg > self.axis[2] * -1 - stop
        else:
            r = deg > self.axis[2] - stop
        while r:
            deg = self.sensors.yaw()
            if deg < 0 and self.axis[2] == 180:
                r = deg > self.axis[2] * -1 - stop
            elif deg > 0 and self.axis[2] == -180:
                r = deg > self.axis[2] * -1 - stop
            else:
                r = deg > self.axis[2] - stop

        if self.axis[2] == -180:
            self.axis[2] = 180
        self.axis[2] -= 90
        print(self.axis[2])
        self.check()
        sleep(0.5)

    def take_package(self, coords):
        self.arm.move_to(coords)
        print(self.arm.setEffector(1))
        self.arm.confort()

    def drop_package(self):
        p = simxGetObjectPosition(self.clientID, self.backpack, -1, simx_opmode_blocking)[1]
        p[2] += 0.2
        self.arm.direct([-87.3, 44.64, 164], unit='deg')
        self.arm.setEffector(0)
        sleep(1)
        self.arm.forward()

    def check(self):
        deg = self.sensors.yaw()
        if np.abs(deg - self.axis[2]) > 0.75:
            self.legs.stop()

            if deg < 0 and self.axis[2] == 180:
                r = deg - self.axis[2] * -1
            elif deg > 0 and self.axis[2] == -180:
                r = deg - self.axis[2] * -1
            else:
                r = deg - self.axis[2]
            if r < 0:
                self.corr += np.abs(r)
                self.legs.turn_left(0.5, False)
                sleep(0.1 * np.abs(r))
                self.legs.stop()
            else:
                self.corr += np.abs(r)
                self.legs.turn_right(0.5, False)
                sleep(0.1 * np.abs(r))
                self.legs.stop()
            self.check()

    def check_proximity(self, op):
        distance = self.sensors.getDistance(self.psensor)
        dist_l = self.sensorl.getDistance(self.sensor_left)
        dist_r = self.sensorr.getDistance(self.sensor_right)

        if (op == 1):  # forward
            if (distance > 0 and distance < 0.8):
                self.legs.turn_right(5, False, self)
            else:
                self.legs.forward(10, self)
        elif op == 2:  # right
            if (distance > 0 and distance < 0.8):
                self.legs.turn_left(5, False, self)
            else:
                self.legs.forward(10, self)

    def distance_side(self):
        dist_l = self.sensorl.getDistance(self.sensor_left)
        dist_r = self.sensorr.getDistance(self.sensor_right)
        dist = self.sensors.getDistance(self.psensor)
        print('laterals -----------------')
        print(dist_l)
        print(dist_r)


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
