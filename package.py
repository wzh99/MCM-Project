# package.py

import judge as jd
import copy as cp
import numpy as np
import numpy.random as rd
import functools as fc

class Placeable:
    def __init__(self, size):
        self.size = size
        self.volume = self.size[0] * self.size[1] * self.size[2]

class Bay(Placeable):
    def __init__(self, size):
        Placeable.__init__(self, size)

BAY_1 = Bay([8, 10, 14])
BAY_2 = Bay([24, 20, 20])

class Drone(Placeable):
    def __init__(self, size, payload, speed, time, video, bay):
        Placeable.__init__(self, size)
        self.payload = payload
        self.speed = speed
        self.time = time
        self.video = video
        self.bay = bay

DRONES = [
    # Drone([45, 45, 25], 3.5, 40, 35, True, BAY_1), # A
    Drone([30, 30, 22], 8, 79, 40, True, BAY_1), # B
    Drone([60, 50, 30], 14, 64, 35, True, BAY_2), # C
    Drone([25, 20, 25], 11, 60, 18, True, BAY_1), # D
    Drone([25, 20, 27], 15, 60, 15, True, BAY_2), # E
    Drone([40, 40, 25], 22, 79, 24, False, BAY_2), # F
    Drone([32, 32, 17], 20, 64, 16, True, BAY_2) # G
]

NUM_DRONES_PER_CONTAINER = 36

def packageContainer():
    # Define function that map samples to container layout
    def samplesToIndices(samples):
        indices = list(map(lambda s: int(s * len(DRONES)), samples))
        indices.sort(key=lambda i: DRONES[i].volume + DRONES[i].bay.volume)
        # Try and judge
        popped = 0
        while len(indices) > 0:
            print(indices)
            # Add drone and bay to placeable list
            droneLst = list(map(lambda i: DRONES[i], indices))
            placeLst = list(map(lambda d: d.size, droneLst))
            placeLst.extend(list(map(lambda d: d.bay.size, droneLst)))
            # Judge if the container can pack them items
            if jd.packing3d(placeLst):
                return indices
            else:
                return []
                # Wrap samples and remove an element
                #sp = samples[popped] * 10
                #sp = sp - np.floor(sp)
                #indices.pop(int(sp * len(droneLst)))
                #popped += 1

    def containerUtilization(indices):
        if len(indices) == 0:
            return 0
        volContainer = jd.length * jd.width * jd.height
        volPackageList = list(map(lambda i: DRONES[i].volume + DRONES[i].bay.volume, 
            indices))
        volUsed = fc.reduce(lambda x, y: x + y, volPackageList)
        return volUsed / volContainer

    def packageStrategy(indices):
        indicesSet = set(indices)
        pkgDict = {}
        for i in indicesSet:
            pkgDict.update({i: indices.count(i)})
        return pkgDict

    def sample():
        pLarge = 0.7
        sigma = 0.1
        nStrat = 20
        dim = NUM_DRONES_PER_CONTAINER
        func = lambda s: containerUtilization(samplesToIndices(s))

        def wrap(val, low, high):
            step = high - low
            ret = []
            for v in val:
                if v < low:
                    while v < low:
                        v += step
                elif v >= high:
                    while v >= high:
                        v -= step
                ret.append(v)
            return np.array(ret)

        def mutate(sample, dim):
            if rd.rand() < pLarge: # large step
                return rd.rand(dim)
            else: # small step
                return wrap(sample + rd.randn(dim) * sigma, 0, 1)

        prevSample = rd.rand(dim)
        prevVal = func(prevSample)
        count = 0
        while count < nStrat:
            newSample = mutate(prevSample, dim)
            newVal = func(newSample)
            if newVal < prevVal:
                if prevVal == 0 or rd.rand() > newVal / prevVal: # newVal = preVal = 0, must try again
                    continue
            # otherwise accept
            prevSample = newSample
            prevVal = newVal
            indices = samplesToIndices(newSample)
            if len(indices) != 0:
                print(packageStrategy(indices), containerUtilization(indices))
            count += 1

    sample()

if __name__ == '__main__':
    packageContainer()