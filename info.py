# info.py

import numpy as np

BOUND = np.array([[-67.293988, 17.897988], [-65.568656, 18.539222]])

class Placeable:
    def __init__(self, size):
        self.size = size
        self.volume = self.size[0] * self.size[1] * self.size[2]

class Medicals:
    def __init__(self, weight, size):
        self.weight = weight
        self.size = size

MEDICALS = [
    Medicals(2, [14, 7, 5]), 
    Medicals(2, [5, 8, 5]),
    Medicals(3, [12, 7, 4])
]

class Hospital:
    def __init__(self, loc, req):
        self.location = loc
        self.requirement = req

HOSPITALS = [
    Hospital([-65.65, 18.33], [1, 0, 1]),
    Hospital([-66.03, 18.22], [2, 0, 1]),
    Hospital([-66.07, 18.44], [1, 1, 0]),
    Hospital([-66.16, 18.40], [2, 1, 2]),
    Hospital([-66.73, 18.47], [1, 0, 0])
]

class Bay(Placeable):
    def __init__(self, size):
        Placeable.__init__(self, size)

    def load(self, pkgList):
        self.packages = pkgList # a list representing medical package indices
        self.weight = self.totalWeight()

    def totalWeight(self):
        wt = 0
        for i in range(len(MEDICALS)):
            wt += MEDICALS[i].weight * self.packages[i]
        return wt

BAY_1 = Bay([8, 10, 14])
BAY_2 = Bay([24, 20, 20])

class Drone(Placeable):
    def __init__(self, size, payload, speed, time, video, bay):
        Placeable.__init__(self, size)
        self.payload = payload
        self.speed = speed / 111 # speed in deg/hr
        self.emptyTime = time / 60 # time in hrs
        self.video = video
        self.bay = bay

    def load(self, pkgList):
        self.bay.load(pkgList)
        k = 1500 / 60
        self.fullTime = k / (k / self.emptyTime + self.bay.weight)

DRONES = [
    # Drone([45, 45, 25], 3.5, 40, 35, True, BAY_1), # A is abandeoned
    Drone([30, 30, 22], 8, 79, 40, True, BAY_1), # B: 0
    Drone([60, 50, 30], 14, 64, 35, True, BAY_2), # C: 1
    Drone([25, 20, 25], 11, 60, 18, True, BAY_1), # D: 2
    Drone([25, 20, 27], 15, 60, 15, True, BAY_2), # E: 3
    Drone([40, 40, 25], 22, 79, 24, False, BAY_2), # F: 4
    Drone([32, 32, 17], 20, 64, 16, True, BAY_2) # G: 5
]

NUM_DRONES_PER_CONTAINER = 36