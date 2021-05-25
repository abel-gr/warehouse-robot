import numpy as np
import cv2
from sim import *
from time import sleep
from math import pi, floor, ceil, radians, degrees, atan2, acos, sqrt, cos, sin
import OCR_Lite as OCR
import matplotlib.pyplot as plt

from fuzzywuzzy import fuzz


class Image:
    def __init__(self, mat, res):
        self.matrix = np.reshape(np.array(mat, dtype=np.uint8), (res[0], res[1], 3))
        self.matrix = cv2.cvtColor(self.matrix, cv2.COLOR_RGB2BGR)
        self.resolution = res
        self.gray = cv2.cvtColor(self.matrix, cv2.COLOR_RGB2GRAY)

    def __getitem__(self, tup):
        return self.matrix[tup[0], tup[1]]

    def predict(self):
        cv2.imwrite('pre-segment.jpg', self.matrix)
        s = OCR.segment(self.gray)
        if not hasattr(s, "__len__"):
            return ""

        plt.figure(1)
        plt.imshow(s, 'gray')
        plt.show()
        cv2.imwrite('post-segment.jpg', s)
        text = OCR.OCR(s)

        return text

    def show_gray(self):
        plt.figure(1)
        plt.imshow(self.gray, 'gray')
        plt.show()

    def show(self):
        plt.figure(1)
        plt.imshow(self.matrix)
        plt.show()

    def mirror(self):
        self.matrix = self.matrix[::-1, :, :]
        self.gray = cv2.cvtColor(self.matrix, cv2.COLOR_RGB2GRAY)


class Package:
    def __init__(self, slot):
        self.slot = slot
        self.id = ""


class Sensors:
    def __init__(self, clientID, cam, psensor, body):
        self.clientID = clientID
        self.cam = cam
        self.psensor = psensor
        self.body = body

        print(psensor)

    def getImage(self):
        retCode, res, image = simxGetVisionSensorImage(self.clientID, self.cam, 0, simx_opmode_oneshot_wait)
        return Image(image, res)

    def getDistance(self, t_sensor):
        retCode, detectionState, detectedPoint, detectedObjectHandle, detectedSurfaceNormalVector = simxReadProximitySensor(
            self.clientID, t_sensor, simx_opmode_blocking)
        print(retCode)
        sensor_val = -1
        if detectionState:
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

    def forward(self, speed):
        simxSetJointTargetVelocity(self.clientID, self.left_wheel, speed, simx_opmode_oneshot)
        simxSetJointTargetVelocity(self.clientID, self.right_wheel, speed, simx_opmode_oneshot)

    def turn_left(self, speed):
        ret = simxSetJointTargetVelocity(self.clientID, self.left_wheel, speed * 1.1, simx_opmode_streaming)
        ret = simxSetJointTargetVelocity(self.clientID, self.right_wheel, -speed, simx_opmode_streaming)

    def turn_right(self, speed):
        ret = simxSetJointTargetVelocity(self.clientID, self.left_wheel, -speed, simx_opmode_streaming)
        ret = simxSetJointTargetVelocity(self.clientID, self.right_wheel, speed, simx_opmode_streaming)

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

        b = simxGetJointPosition(self.clientID, self.base, simx_opmode_blocking)[1]
        s = simxGetJointPosition(self.clientID, self.shoulder, simx_opmode_blocking)[1]
        e = simxGetJointPosition(self.clientID, self.elbow, simx_opmode_blocking)[1]
        w = simxGetJointPosition(self.clientID, self.wrist, simx_opmode_blocking)[1]

        self.angles = [degrees(b), degrees(s), degrees(e), degrees(w)]

    def setEffector(self, val):
        # función que acciona el efector final remotamente
        # val es Int con valor 0 ó 1 para desactivar o activar el actuador final.
        res, retInts, retFloats, retStrings, retBuffer = simxCallScriptFunction(self.clientID,
                                                                                "suctionPad",
                                                                                sim_scripttype_childscript,
                                                                                "setEffector", [val], [], [], "",
                                                                                simx_opmode_blocking)
        return res

    def move_to(self, coords):
        """
        l1 = 0.2659
        l2 = 0.2585
        l3 = 0.1415
        l4 = 0.0750
        """
        try:
            p = simxGetObjectPosition(self.clientID, self.base, -1, simx_opmode_blocking)[1]
            H = 265.9
            b = 258.5
            ab = 141.5
            m = 75

            x = (coords[0] - p[0]) * 1000
            y = (coords[1] - p[1]) * 1000
            z = (coords[2]) * 1000
            cabGrados = 0
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
            # self.confort()
            self.direct([Axis1Grados, Axis2Grados, Axis3Grados, -60], unit='deg')
            sleep(0.2)
            Axis4Grados = 180 - Axis2Grados - Axis3Grados
            # print(Axis1Grados, Axis2Grados, Axis3Grados, Axis4Grados)
            self.direct([Axis1Grados, Axis2Grados, Axis3Grados, Axis4Grados], unit='deg')

        except:
            print("Posició no accessible")

    def direct(self, angles, unit='rad'):
        if unit == 'rad':
            if len(angles) > 3:
                retCode = simxSetJointTargetPosition(self.clientID, self.wrist, angles[3], simx_opmode_oneshot)
                self.angles[3] = degrees(angles[3])
            retCode = simxSetJointTargetPosition(self.clientID, self.base, (angles[0] + pi), simx_opmode_oneshot)
            self.angles[0] = degrees(angles[0] + pi)
            sleep(0.5)

            retCode = simxSetJointTargetPosition(self.clientID, self.elbow, angles[2], simx_opmode_oneshot)
            self.angles[2] = degrees(angles[2])
            retCode = simxSetJointTargetPosition(self.clientID, self.shoulder, angles[1],
                                                 simx_opmode_oneshot)
            sleep(0.2)
            self.angles[1] = degrees(angles[1])
            sleep(0.5)

        else:
            if len(angles) > 3:
                retCode = simxSetJointTargetPosition(self.clientID, self.wrist, radians(angles[3]),
                                                     simx_opmode_oneshot)
                self.angles[3] = angles[3]

            retCode = simxSetJointTargetPosition(self.clientID, self.base, (radians(angles[0]) + pi),
                                                 simx_opmode_oneshot)
            sleep(0.2)

            retCode = simxSetJointTargetPosition(self.clientID, self.elbow, radians(angles[2]),
                                                 simx_opmode_oneshot)
            sleep(0.3)
            retCode = simxSetJointTargetPosition(self.clientID, self.shoulder, radians(angles[1]),
                                                 simx_opmode_oneshot)
            sleep(0.3)
            self.angles[0] = angles[0]
            self.angles[1] = angles[1]
            self.angles[2] = angles[2]

        return retCode

    def confort(self):

        retCode = simxSetJointTargetPosition(self.clientID, self.shoulder, radians(35),
                                             simx_opmode_oneshot)

        retCode = simxSetJointTargetPosition(self.clientID, self.elbow, radians(127.7839641973666),
                                             simx_opmode_oneshot)
        sleep(0.1)
        retCode = simxSetJointTargetPosition(self.clientID, self.wrist, radians(0),
                                             simx_opmode_oneshot)
        self.angles[3] = 0
        self.angles[1] = 35
        self.angles[2] = 127.7839641973666

    def forward(self):
        self.direct([-90, -60, -130, 100], unit='deg')


class Brain:  # It will be the main class where all the other class will be connected. It will also do all the work
    # related with connecting the code with the simulator
    def __init__(self):
        self.corr = 0
        self.clientID = connect(19999)
        assert self.clientID != -1
        self.axis = np.array([0, 0, 0])
        self.arm_home = [-90, 90, 0]
        ret_codes = np.zeros(15)
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
        ret_codes[11], self.backpack1 = simxGetObjectHandle(self.clientID, 'Backpack1', simx_opmode_blocking)
        ret_codes[12], self.backpack2 = simxGetObjectHandle(self.clientID, 'Backpack2', simx_opmode_blocking)

        assert not all(ret_codes)
        self.legs = Legs(self.clientID, self.left_wheel, self.right_wheel)
        self.arm = Arm(self.clientID, self.base, self.shoulder, self.elbow, self.wrist, self.arm_tip)
        self.sensors = Sensors(self.clientID, self.cam, self.psensor, self.obj)

        self.boxes = [Package(1), Package(2)]
        self.check()
        print("Initialization completed, connection established")

    def take_photo(self, coords):
        # self.go_to(coords)
        self.check()
        pos = simxGetObjectPosition(self.clientID, self.base, -1, simx_opmode_blocking)[1]

        offsetx = 0.0008
        offsety = 0
        x, y, z = 0, 0, 0

        if coords[0] < pos[0]:
            x = coords[0] - offsetx
        else:
            x = coords[0] + offsetx
        y = coords[1] + offsety
        z = coords[2] + 0.0531 + 0.15

        self.arm.move_to([x, y, z])
        im = self.sensors.getImage()
        im.mirror()
        p = im.predict()

        self.check()

        return p

    def save_package(self, coords, slot):
        info = self.take_photo(coords)
        info = info.replace(' ', '')
        info = info.replace('O', '0')
        info = info.replace('\n', '')
        
        print(info)
        self.boxes[slot-1].id = info
        self.take_package(coords, slot)

    def take_package(self, coords, slot):

        # mirar paquet
        #   Guardar info paquet
        # llegir paquet
        self.check()
        pos = simxGetObjectPosition(self.clientID, self.base, -1, simx_opmode_blocking)[1]

        if coords[0] < pos[0]:
            coords[0] += 0.041119
        else:
            coords[0] -= 0.041119

        coords[2] += 0.05 + 0.0031 + 0.045

        self.arm.move_to(coords)
        self.arm.setEffector(1)
        sleep(0.25)
        self.arm.confort()
        sleep(0.25)

        if slot == 1:
            pck = simxGetObjectPosition(self.clientID, self.backpack1, -1, simx_opmode_blocking)[1]
        if slot == 2:
            pck = simxGetObjectPosition(self.clientID, self.backpack2, -1, simx_opmode_blocking)[1]

        self.check()
        pos = simxGetObjectPosition(self.clientID, self.base, -1, simx_opmode_blocking)[1]

        if pck[0] < pos[0]:
            pck[0] += 0.025
            # pck[1] += 0.1
        else:
            pck[0] -= 0.025
            # pck[1] -= 0.1

        pck[2] += 0.05 + 0.0031 + 0.09

        self.arm.move_to(pck)
        self.arm.setEffector(0)
        sleep(0.5)
        self.arm.confort()

    def drop_package(self, coords, slot):
        if slot == 1:
            pck = simxGetObjectPosition(self.clientID, self.backpack1, -1, simx_opmode_blocking)[1]
        if slot == 2:
            pck = simxGetObjectPosition(self.clientID, self.backpack2, -1, simx_opmode_blocking)[1]

        self.boxes[slot-1].id = ""
        self.check()
        pos = simxGetObjectPosition(self.clientID, self.base, -1, simx_opmode_blocking)[1]

        if pck[0] < pos[0]:
            pck[0] += 0.025
            # pck[1] += 0.1
        else:
            pck[0] -= 0.025
            # pck[1] -= 0.1

        pck[2] += 0.05 + 0.0031 + 0.08

        self.arm.move_to(pck)
        self.arm.setEffector(1)
        sleep(0.5)
        self.arm.direct([self.arm.angles[0], 35, 127.7839641973666, self.arm.angles[3]], unit='deg')
        sleep(0.5)
        self.arm.move_to(coords)
        self.arm.setEffector(0)
        sleep(0.5)

        self.arm.confort()
        self.arm.forward()

    def go_to(self, coords):
        if self.arm.angles[0] != -90:
            self.arm.forward()
        if self.axis[2] == 180 or self.axis[2] == 0:
            ax = 1
        else:
            ax = 0

        target = coords[ax]
        pos = simxGetObjectPosition(self.clientID, self.base, -1, simx_opmode_blocking)[1][ax]
        dist = abs(target - pos)
        speed = min(15, dist + 5)
        while dist > 0.1:
            self.legs.forward(speed)
            estimated_time = dist / (speed * 0.019)
            print("Dist = ", dist, "Estimated Time", estimated_time)
            self.legs.stop()
            if estimated_time > 1:
                for i in range(0, floor(estimated_time * 3)):
                    self.legs.forward(speed)
                    sleep(0.15)
                    self.check()
            else:
                sleep(estimated_time)
            pos = simxGetObjectPosition(self.clientID, self.base, -1, simx_opmode_blocking)[1][ax]
            dist = abs(target - pos)
            speed = min(15, dist + 5)

        if dist > 0:
            self.legs.forward(5)
            sleep(dist / (speed * 0.019))
            self.legs.stop()

    def check(self):
        deg = self.sensors.yaw()
        if deg - self.axis[2] > 1 or deg - self.axis[2] < -0.75:
            self.legs.stop()

            if deg < 0 and self.axis[2] == 180:
                r = deg - self.axis[2] * -1
            elif deg > 0 and self.axis[2] == -180:
                r = deg - self.axis[2] * -1
            else:
                r = deg - self.axis[2]
            if r < 0:
                self.corr += np.abs(r)
                self.legs.turn_left(0.5)
                sleep(0.1 * np.abs(r))
                self.legs.stop()
            else:
                self.corr += np.abs(r)
                self.legs.turn_right(0.5)
                sleep(0.1 * np.abs(r))
                self.legs.stop()
            self.check()
