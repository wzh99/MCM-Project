# pop.py
import cv2
import numpy as np

class Population:
    def __init__(self, path, longBnd, latiBnd):
        self.imgRgb = cv2.imread(path)
        self.imgHsv = cv2.cvtColor(self.imgRgb, cv2.COLOR_BGR2HSV)
        self.longBnd = longBnd # from west(smaller) to east(larger)
        self.latiBnd = latiBnd # from south(smaller) to north(larger)

    def estimateDensity(self, pt):
        x, y = self.__locToPixel(pt[0], pt[1])
        hsv = self.imgHsv[y, x]
        if hsv[1] < 10: # indicate that it's white color
            return 0
        return 4.889e4 * np.exp(-0.02432 * hsv[0]) # convert to population density

    def __locToPixel(self, longi, lati):
        x = self.__rangeMap(longi, self.longBnd, [0, self.imgRgb.shape[1] - 1])
        y = self.__rangeMap(lati, self.latiBnd, [self.imgRgb.shape[0] - 1, 0])
        return int(x), int(y)

    @staticmethod
    def __rangeMap(val, valRange, newRange):
        t = (val - valRange[0]) / (valRange[1] - valRange[0])
        if t < 0 or t > 1:
            return 0
        return (1 - t) * newRange[0] + t * newRange[1]

if __name__ == '__main__':
    pop = Population("img/pop_den_trace.jpg", [120.85, 121.98], [30.67, 31.51])
    print(pop.estimateDensity([121.5, 31.3]))
