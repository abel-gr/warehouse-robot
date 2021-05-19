import numpy as np
import cv2
from sim import *
from time import sleep
from sympy import *
from sympy.physics.vector import init_vprinting
import math
from random import randint

init_vprinting(use_latex='mathjax', pretty_print=False)
from sympy.physics.mechanics import dynamicsymbols

theta1, theta2, theta3, theta4, d3, lc, la, lb, alpha, a, d = dynamicsymbols('theta1 theta2 theta3 theta4 d3 lc la lb alpha a d')


class Image:
    def __init__(self, mat, res):
        self.matrix = np.reshape(np.array(mat, dtype=np.uint8), (res[0], res[1], 3))
        self.matrix = cv2.cvtColor(self.matrix, cv2.COLOR_RGB2BGR)
        self.resolution = res
        self.gray = cv2.cvtColor(self.matrix, cv2.COLOR_RGB2GRAY)

    def __getitem__(self, tup):
        return self.matrix[tup[0], tup[1]]


class Sensors:
    def __init__(self, clientID, cam, psensor, bdummy, fdummy, body, sensor_left, sensor_right):
        self.clientID = clientID
        self.cam = cam
        self.psensor = psensor
        self.bdummy = bdummy
        self.fdummy = fdummy
        self.body = body
        self.sensorl = sensor_left
        self.sensorr = sensor_right


        print(psensor)

    def getImage(self):
        retCode, res, image = simxGetVisionSensorImage(self.clientID, self.cam, 0, simx_opmode_oneshot_wait)
        return Image(image, res)

    def getDistance(self,t_sensor):
        retCode, detectionState, detectedPoint, detectedObjectHandle, detectedSurfaceNormalVector = simxReadProximitySensor(
            self.clientID, t_sensor, simx_opmode_blocking)
        print(retCode)
        sensor_val=-1
        if detectionState==True:
            sensor_val = np.linalg.norm(detectedPoint)
            print("distacia al objeto: ", sensor_val)
        else:
           print("No ha detectado objeto")
        return sensor_val
        
    def yaw(self):
        ret, bd = simxGetObjectOrientation(self.clientID, self.body, -1, simx_opmode_blocking)
        #print(np.rad2deg(bd[2]))
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
        
        self.sensors = Sensors(self.clientID, self.cam, self.psensor, self.bdummy, self.fdummy, self.obj, self.sensor_left, self.sensor_right)

    def forward(self, speed,b):
        op=1
        simxSetJointTargetVelocity(self.clientID, self.left_wheel, speed, simx_opmode_streaming)
        simxSetJointTargetVelocity(self.clientID, self.right_wheel, speed, simx_opmode_streaming)
        b.distance_side()
        b.check_proximity(op)

    def turn_left(self, speed,required,b):
        distance=self.sensors.getDistance(self.psensor)
        while(distance>0.7 or distance==-1 or required):
            distance=self.sensors.getDistance(self.psensor)
            ret = simxSetJointTargetVelocity(self.clientID, self.left_wheel, speed, simx_opmode_streaming)
            ret = simxSetJointTargetVelocity(self.clientID, self.right_wheel, -speed, simx_opmode_streaming)
            if required:
                sleep(1)
            required=False
            sleep(0.3)
            b.check_proximity(1)
        
    def turn_right(self, speed,required,b):
        distance=self.sensors.getDistance(self.psensor)
        while(distance>0.7 or distance==-1 or required):
            distance=self.sensors.getDistance(self.psensor)
            ret = simxSetJointTargetVelocity(self.clientID, self.left_wheel, -speed, simx_opmode_streaming)
            ret = simxSetJointTargetVelocity(self.clientID, self.right_wheel, speed, simx_opmode_streaming)
            if required:
                sleep(1)
            required=False
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
        l1 = -0.25
        l2 = -0.175
        l3 = l2
        l4 = 0.0750

        eq1 = -0.175*sin(theta2+theta3)*sin(theta1)*cos(90)-0.25*sin(theta2+theta3+theta4)*sin(theta1)*cos(90)-0.25*sin(theta1)*sin(theta2)*cos(90)+l1*cos(theta2+theta3)*cos(theta1)+0.075*cos(theta2+theta3+theta4)*cos(theta1)+l1*cos(theta1)*cos(theta2) -coords[0]
        eq2 = 0.175*sin(theta2+theta3)*cos(90)*cos(theta1)+0.075*sin(theta2+theta3+theta4)*cos(90)*cos(theta1)+0.175*sin(theta1)*cos(theta2+theta3)+0.075*sin(theta1)*cos(theta2+theta3+theta4)+0.175*sin(theta1)*cos(theta2)+0.175*sin(theta2)*cos(90)*cos(theta1) - coords[1]
        eq3 = 0.175*sin(90)*sin(theta2+theta3)+0.075*sin(90)*sin(theta2+theta3+theta4)+0.175*sin(90)*sin(theta2)+0.25 - coords[2]


        #eq3 = 0.105 - d3 - coords[2]

        precs = [30, 25, 20, 15, 10, 5]
        for p in precs:
            try:
                q = nsolve((eq1, eq2, eq3), (theta1, theta2, theta3), (1, 1, 1), prec=p)
            except:
                if p == precs[-1]:
                    print('No se encuentra solución para: ', coords[0], ", ", coords[1], ", ", coords[2])
                    q = [0, 0, 0, 0]

        #retCode = simxSetJointTargetPosition(self.clientID, self.base, q[0], simx_opmode_oneshot)
        retCode = simxSetJointTargetPosition(self.clientID, self.shoulder, q[0], simx_opmode_oneshot)
        retCode = simxSetJointTargetPosition(self.clientID, self.elbow, -q[1], simx_opmode_oneshot)
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
        self.corr = 0
        self.clientID = connect(19999)
        assert self.clientID != -1
        self.axis = np.array([0, 0, 0])

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
        ret_codes[11], self.bdummy = simxGetObjectHandle(self.clientID, 'Back_dummy', simx_opmode_blocking)
        ret_codes[12], self.fdummy = simxGetObjectHandle(self.clientID, 'Front_dummy', simx_opmode_blocking)
        ret_codes[13], self.sensor_left = simxGetObjectHandle(self.clientID, 'sensor_left', simx_opmode_blocking)
        ret_codes[14], self.sensor_right = simxGetObjectHandle(self.clientID, 'sensor_right', simx_opmode_blocking)
        

        assert not all(ret_codes)

        self.arm = Arm(self.clientID, self.base, self.shoulder, self.elbow, self.wrist, self.arm_tip)
        self.legs = Legs(self.clientID, self.left_wheel, self.right_wheel)
        self.sensors = Sensors(self.clientID, self.cam, self.psensor, self.bdummy, self.fdummy, self.obj, self.sensor_left, self.sensor_right)
        self.sensorl = Sensors(self.clientID, self.cam, self.sensor_left, self.bdummy, self.fdummy, self.obj, self.sensor_left, self.sensor_right)
        self.sensorr = Sensors(self.clientID, self.cam, self.sensor_right, self.bdummy, self.fdummy, self.obj, self.sensor_left, self.sensor_right)



        print("Initialization completed, connection established")

    def turn_left(self):
        self.check()
        self.legs.turn_left(1,False)
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
            #self.check()

    def turn_right(self):
        self.check()
        self.legs.turn_right(1,False)
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
                self.legs.turn_left(0.5,False)
                sleep(0.1 * np.abs(r))
                self.legs.stop()
            else:
                self.corr += np.abs(r)
                self.legs.turn_right(0.5,False)
                sleep(0.1 * np.abs(r))
                self.legs.stop()
            self.check()

    def check_proximity(self,op):
        distance=self.sensors.getDistance(self.psensor)
        dist_l=self.sensorl.getDistance(self.sensor_left)
        dist_r=self.sensorr.getDistance(self.sensor_right)
        
        if(op==1):#forward
            if (distance > 0 and distance < 0.8):
                self.legs.turn_right(5,False,self)
            else:
                self.legs.forward(10,self) 
        elif op==2:#right
            if (distance > 0 and distance < 0.8):
                self.legs.turn_left(5,False,self)
            else:
                self.legs.forward(10,self)  


    def distance_side(self):
        dist_l=self.sensorl.getDistance(self.sensor_left)
        dist_r=self.sensorr.getDistance(self.sensor_right)
        dist=self.sensors.getDistance(self.psensor)
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

