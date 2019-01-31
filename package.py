# package.py

import judge as jd
import info

import numpy as np
import numpy.random as rd
import functools as fc
import copy as cp

MEDICALS = info.MEDICALS

BAY_1 = info.BAY_1
BAY_2 = info.BAY_2

DRONES = info.DRONES

NUM_DRONES_PER_CONTAINER = info.NUM_DRONES_PER_CONTAINER

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