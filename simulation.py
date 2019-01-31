# simulation.py

import numpy as np 
import numpy.random as rd 
import copy as cp
import pandas as pd
import functools as fc

import info
import route as rt
from mtr import Metropolis

MEDICALS = info.MEDICALS
HOSPITALS = info.HOSPITALS
BAY_1 = info.BAY_1
BAY_2 = info.BAY_2
DRONES = info.DRONES

def distSq(p1, p2):
    return (p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2

class Container:
    def __init__(self, loc, nDrones):
        self.location = loc
        self.drones = []
        for i in range(len(DRONES)):
            for _ in range(nDrones[i]):
                self.drones.append(newDrone(i))

def newDrone(idx):
    drone = cp.deepcopy(DRONES[idx])
    return drone

DELIVERY_CONTAINER_DRONES = [29, 9, 0, 0, 0, 0]
VIDEO_CONTAINER_DRONES = [20, 9, 0, 0, 2, 0]

CONTAINERS = [
    Container([-65.6848, 18.2934], VIDEO_CONTAINER_DRONES), # on the north-east
    Container([-66.071, 18.32], DELIVERY_CONTAINER_DRONES), # in the middle
    Container([-66.7421, 18.3932], VIDEO_CONTAINER_DRONES) # on the north-west
]

BAY_1_CANDIDATES = np.array(pd.read_excel("data/bay.xlsx", sheet_name="bay1",
    usecols=range(1, 4), convert_float=True))
BAY_2_CANDIDATES = np.array(pd.read_excel("data/bay.xlsx", sheet_name="bay2",
    usecols=range(1, 4), convert_float=True))

def reuseSample(sp):
    step = 13
    nsp = sp * step
    return nsp - np.floor(nsp)

def simulate():
    def samplesToConfig(samples, verbose):
        config = cp.deepcopy(CONTAINERS)
        delivery = np.zeros((len(HOSPITALS), len(MEDICALS)))
        roadMap = cp.deepcopy(rt.roadMap)
        initalArea = roadMap.count()
        coverage = 0
        if verbose:
            visMap = cp.deepcopy(roadMap)

        nSp = 0
        for iCont in range(3): 
            # Choose container packaging strategy
            container = config[iCont]
            locCtn = container.location
            if verbose:
                print("Container: ", locCtn)

            if iCont == 0 or iCont == 2:
                contArea = roadMap.countAround(locCtn, 0.104260)
                ratio = 1 - np.exp(-2.44 * 29 / 2)
                coverage += contArea / initalArea * ratio
                if verbose:
                    visMap.eraseAround(locCtn, 0.104260 * ratio)

            for drone in container.drones:
                # Choose bay packaging configuration
                if (iCont == 0 or iCont == 2) and drone.size != DRONES[4].size:
                    continue
                bay = drone.bay
                sp = samples[nSp]
                nSp += 1
                if bay.size == BAY_1.size:
                    drone.load(BAY_1_CANDIDATES[int(sp * len(BAY_1_CANDIDATES))])
                    sp = reuseSample(sp)
                else:
                    if iCont == 0:
                        drone.load(BAY_2_CANDIDATES[24])
                    elif iCont == 2:
                        drone.load(BAY_2_CANDIDATES[27])
                    else:
                        while True:
                            idx = int(sp * len(BAY_2_CANDIDATES))
                            drone.load(BAY_2_CANDIDATES[idx])
                            if bay.weight > drone.payload:
                                sp = reuseSample(sp)
                            else:
                                break
                        sp = reuseSample(sp)

                # Choose a hospital that the drone can reach
                time = 1.0 / (1.0 / drone.emptyTime + 1.0 / drone.fullTime)
                r = time * drone.speed
                hosCand = list(filter(lambda h: distSq(h.location, locCtn) < r ** 2, HOSPITALS))
                
                if verbose and len(hosCand) == 0:
                    print("Invalid drone!")
                    print(locCtn)
                    print(drone.__dict__)
                    continue

                hospital = hosCand[int(sp * len(hosCand))]
                sp = reuseSample(sp)
                dist = np.sqrt(distSq(locCtn, hospital.location))
                reachTime = dist / drone.speed

                # Transport packages to hospital and scan roads
                # hosIdx = 0
                for iHos in range(len(HOSPITALS)):
                    if hospital.location == HOSPITALS[iHos].location:
                        hosIdx = iHos
                if verbose:
                    for k in range(len(DRONES)):
                        if DRONES[k].size == drone.size:
                            drnIdx = k
                    print("Drone:", drnIdx, "to hospital:", hosIdx)
                delivery[hosIdx] += np.array(bay.packages)
                midPt = (np.array(locCtn) + np.array(hospital.location)) / 2
                roadMap.eraseAlong(rt.Bezier(np.array([locCtn, midPt, hospital.location])))
                if verbose:
                    visMap.eraseAlong(rt.Bezier(np.array([locCtn, midPt, hospital.location])))

                # Try returning route that can cover more loads
                if verbose:
                    # spline computation is time-consuming
                    lMax = drone.speed * drone.emptyTime * (1 - reachTime / drone.fullTime)
                    dirct = np.array(hospital.location) - np.array(locCtn)
                    nSeg = 10
                    rotatedDir = np.array([-dirct[1], dirct[0]])
                    seg = rotatedDir / nSeg
                    
                    maxArea = 0
                    maxIdx = 0
                    for i in range(int(-nSeg / 2), int(nSeg / 2) + 1):
                        pCtrl = midPt + i * seg
                        bez = rt.Bezier(np.array([locCtn, pCtrl, hospital.location]))
                        bezLen = bez.length
                        if bezLen >= lMax:
                            continue
                        area = visMap.countAlong(bez)
                        if area > maxArea:
                            maxArea = area
                            maxIdx = i
                    visMap.eraseAlong(rt.Bezier(np.array([locCtn, midPt + maxIdx * seg, hospital.location])))
                
                
        coverage += (initalArea - roadMap.count()) / initalArea
        coverage += 0.03 
        if verbose:
            visMap.write("img/coverage.png")
            coverage = (initalArea - visMap.count()) / initalArea
        return delivery, coverage

    def evaluate(delivery, coverage):
        dlv = 1e10
        for i in range(len(HOSPITALS)):
            for j in range(len(MEDICALS)):
                if HOSPITALS[i].requirement[j] == 0:
                    continue
                dlv = min(float(dlv), float(delivery[i, j] / HOSPITALS[i].requirement[j]))
        return 0.5 * (2 / (1 + np.exp(-dlv / 1.4)) - 1) + 0.5 * coverage

    def function(samples):
        deliv, covr = samplesToConfig(samples, False)
        return evaluate(deliv, covr)

    m = Metropolis(0.1, 0.005)
    val, samples = m.anneal(function, 50, 0.9, 0.1, 0.07, 10)
    #samples = rd.rand(50)
    print(samplesToConfig(samples, True))

if __name__ == '__main__':
    simulate()