# route.py

import cv2
import numpy as np

import info

BOUND = info.BOUND

def distSq(pt1, pt2):
    return (pt1[0] - pt2[0]) ** 2 + (pt1[1] - pt2[1]) ** 2

class Bezier:
    def __init__(self, pts):
        self.pt = pts
        # Perform integration
        nInteg = 50
        dt = 1 / nInteg
        prevP = self.pt[0]
        len = 0
        for i in range(nInteg):
            newP = self.at((i + 1) * dt)
            len += np.sqrt(distSq(newP, prevP))
            prevP = newP
        self.length = len

    def at(self, t):
        return (1-t)**2 * self.pt[0] + 2*t*(1-t) * self.pt[1] + t**2 * self.pt[2]


class RoadMap:
    def __init__(self, path):
        rgb = cv2.imread(path)
        gray = cv2.cvtColor(rgb, cv2.COLOR_BGR2GRAY)
        _, self.img = cv2.threshold(gray, 64, 255, cv2.THRESH_BINARY)
        self.bnd = BOUND.transpose()
        self.pixelPerDeg = np.mean(np.array([self.img.shape[1], self.img.shape[0]]) / np.array([BOUND[1, 0] - BOUND[0, 0], BOUND[1, 1] - BOUND[0, 1]]))

    def count(self):
        cnt = 0
        for i in range(self.img.shape[0]):
            for j in range(self.img.shape[1]):
                if self.img[i, j] > 0:
                    cnt += 1
        return cnt

    def countAround(self, pt, deg):
        return len(self._getAround(pt, deg * self.pixelPerDeg))

    def _getAround(self, pt, radius):
        imgPtList = []
        x, y = self._locToPixel(pt[0], pt[1])
        for i in range(y - int(radius), y + int(radius)):
            for j in range(x - int(radius), x + int(radius)):
                if i >= self.img.shape[0] or j >= self.img.shape[1]:
                    continue
                if distSq([x, y], [j, i]) <= radius ** 2 and self.img[i, j] > 0:
                    imgPtList.append([j, i])
        return imgPtList

    def eraseAround(self, pt, radius):
        ptList = self._getAround(pt, radius * self.pixelPerDeg)
        self._erase(ptList)

    def _erase(self, imgPtSet):
        for p in imgPtSet:
            self.img[p[1], p[0]] = 0

    def _getAlong(self, bez, radius):
        # Decide segment number
        imgBezPt = []
        for p in bez.pt:
            x, y = self._locToPixel(p[0], p[1])
            imgBezPt.append([x, y])
        imgBez = Bezier(np.array(imgBezPt))
        imgBezLen = imgBez.length
        nSeg = 2 * int(np.ceil(imgBezLen / radius))
        # Count loop
        imgPtSet = set()
        dt = 1 / nSeg
        for seg in range(nSeg):
            lst = self._getAround(bez.at(dt * seg), radius)
            for p in lst:
                imgPtSet.add(tuple(p))
        return imgPtSet

    def countAlong(self, bez, radius = 15):
        st = self._getAlong(bez, radius)
        return len(st)

    def eraseAlong(self, bez, radius = 15):
        st = self._getAlong(bez, radius)
        self._erase(st)

    def show(self):
        cv2.imshow("Road Map", self.img)
        cv2.waitKey(0)

    def write(self, path):
        cv2.imwrite(path, self.img)

    def _locToPixel(self, longi, lati):
        x = self._rangeMap(longi, self.bnd[0], [0, self.img.shape[1] - 1])
        y = self._rangeMap(lati, self.bnd[1], [self.img.shape[0] - 1, 0])
        return int(x), int(y)

    @staticmethod
    def _rangeMap(val, valRange, newRange):
        t = (val - valRange[0]) / (valRange[1] - valRange[0])
        if t < 0 or t > 1:
            return 0
        return (1 - t) * newRange[0] + t * newRange[1]

roadMap = RoadMap("img/roads.png")

if __name__ == '__main__':
    bez = Bezier(np.array([[-66.73, 18.47], [-66.16, 18.40], [-66.07, 18.44]]))
    roadMap.eraseAlong(bez)
    roadMap.show()
    