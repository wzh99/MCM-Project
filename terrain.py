# terrain.py

import info

import cv2
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

BOUND = info.BOUND

class Terrain:
    def __init__(self, path):
        self.imgRgb = cv2.imread(path)
        self.imgHsv = cv2.cvtColor(self.imgRgb, cv2.COLOR_BGR2HSV)
        self.bnd = BOUND.transpose()

    def getHeight(self, pt):
        x, y = self.__locToPixel(pt[0], pt[1])
        hsv = self.imgHsv[y, x]
        if hsv[0] < 10: # indicate that it's black color
            return 0
        return 1.071e4 * np.exp(-0.06058 * hsv[0]) # convert to population density

    def plotHeight(self):
        nStep = 50
        X = np.linspace(BOUND[0, 0], BOUND[1, 0])
        Y = np.linspace(BOUND[0, 1], BOUND[1, 1])
        gX, gY = np.meshgrid(X, Y)
        Z = np.ndarray((nStep, nStep))
        for i in range(nStep):
            for j in range(nStep):
                Z[j, i] = self.getHeight([X[i], Y[j]])
        fig = plt.figure()
        ax = Axes3D(fig)
        ax.plot_surface(gX, gY, Z, rstride=1, cstride=1, cmap=plt.cm.Blues)
        plt.show()

    def __locToPixel(self, longi, lati):
        x = self.__rangeMap(longi, self.bnd[0], [0, self.imgRgb.shape[1] - 1])
        y = self.__rangeMap(lati, self.bnd[1], [self.imgRgb.shape[0] - 1, 0])
        return int(x), int(y)

    @staticmethod
    def __rangeMap(val, valRange, newRange):
        t = (val - valRange[0]) / (valRange[1] - valRange[0])
        if t < 0 or t > 1:
            return 0
        return (1 - t) * newRange[0] + t * newRange[1]

terrain = Terrain("img/terrain.png")

if __name__ == '__main__':
    terrain.plotHeight()
    