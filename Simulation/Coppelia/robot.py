import numpy as np
import cv2
import sim


class Image:
    def __init__(self, mat):
        self.matrix = mat
        self.resolution = (mat.shape[0], mat.shape[1])
        self.gray = cv2.cvtColor(mat, cv2.COLOR_GRAY2RGB)

    def __getitem__(self, tup):
        return self.matrix[tup[0], tup[1]]

class Legs:
    pass


class Brain:  # It will be the main class where all the other class will be connected. It will also do all the work
    # related with connecting the code with the simulator

    def __init__(self, mat):
        self.clientID = sim.connect(19999)
        self.legs = Legs()





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